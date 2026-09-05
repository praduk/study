from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

import study_app.review as review_module
from study_app.app import create_app
from study_app.review import ReviewEngine
from study_app.review_calibration import (
    calibration_reporting_summary,
    new_calibration_state,
    observe_review,
    reporting_model_estimate,
)
from study_app.store import LibraryStore, StoreError

LOCAL_HEADERS = {"origin": "http://127.0.0.1", "x-study-csrf": "local"}


def _grade(
    client: TestClient,
    card_id: str,
    grade: int,
    *,
    elapsed_ms: int,
) -> dict[str, object]:
    revealed = client.post(
        f"/api/review/{card_id}/reveal",
        json={
            "attempt": "A written attempt",
            "confidence": 2,
            "elapsed_ms": elapsed_ms,
            "overt": True,
        },
        headers=LOCAL_HEADERS,
    )
    assert revealed.status_code == 200
    graded = client.post(
        f"/api/review/{card_id}/grade",
        json={"attempt_id": revealed.json()["attempt_id"], "grade": grade},
        headers=LOCAL_HEADERS,
    )
    assert graded.status_code == 200
    return graded.json()


def test_read_only_stats_do_not_rewrite_equivalent_calibration_roundoff(tmp_path):
    store = LibraryStore(tmp_path / "data")
    review = ReviewEngine(store)
    review.queue()
    state = json.loads(review.state_path.read_text(encoding="utf-8"))
    state["calibration"]["models"]["pooled"]["log_weights"][0] += 1e-14
    state["updated_at"] = "preserve-this-value"
    review.state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    before = review.state_path.read_bytes()

    ReviewEngine(store).stats()

    assert review.state_path.read_bytes() == before


def test_calendar_api_reports_schedules_repeated_attempts_and_bayesian_diagnostics(
    settings_factory, monkeypatch: pytest.MonkeyPatch
):
    clock = {"now": datetime(2026, 9, 5, 12, 0, tzinfo=timezone.utc)}
    monkeypatch.setattr(review_module, "_now", lambda: clock["now"])
    app = create_app(settings_factory(), local_mode=True)
    folder = app.state.store.create_folder("Foundations", "foundations", None)
    first = app.state.store.create_entry(
        folder["id"], "df", "First definition", "first", "", "First content"
    )
    second = app.state.store.create_entry(
        folder["id"], "df", "Second definition", "second", "", "Second content"
    )
    app.state.store.create_entry(
        folder["id"], "df", "Unreviewed definition", "unreviewed", "", "New content"
    )

    with TestClient(
        app,
        base_url="http://127.0.0.1",
        client=("127.0.0.1", 50000),
    ) as client:
        cards = client.get("/api/review/queue").json()["cards"]
        card_by_entry = {card["entry_id"]: card for card in cards}
        _grade(client, card_by_entry[first["id"]]["id"], 0, elapsed_ms=60_000)
        clock["now"] += timedelta(minutes=20)
        first_schedule = _grade(
            client, card_by_entry[first["id"]]["id"], 2, elapsed_ms=120_000
        )
        second_schedule = _grade(
            client, card_by_entry[second["id"]]["id"], 2, elapsed_ms=60_000
        )

        state_before = app.state.review.state_path.read_bytes()
        log_before = app.state.review.log_path.read_bytes()
        start = clock["now"].replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=10)
        response = client.get(
            "/api/review/calendar",
            params={"start": start.isoformat(), "end": end.isoformat()},
        )

        assert response.status_code == 200
        assert response.headers["cache-control"] == "no-store"
        assert app.state.review.state_path.read_bytes() == state_before
        assert app.state.review.log_path.read_bytes() == log_before

    payload = response.json()
    assert payload["range"] == {"start": start.isoformat(), "end": end.isoformat()}
    assert [event["entry_id"] for event in payload["events"]] == [
        first["id"],
        second["id"],
    ]
    assert [event["title"] for event in payload["events"]] == [
        "First definition",
        "Second definition",
    ]
    assert payload["events"][0]["canonical_tag"] == "foundations:df:first"
    assert payload["events"][0]["active"] is True
    assert payload["events"][0]["review_enabled"] is True
    assert payload["events"][0]["schedule_at_last_grade"]["due_at"] == first_schedule[
        "due_at"
    ]
    assert payload["events"][1]["schedule_at_last_grade"]["due_at"] == second_schedule[
        "due_at"
    ]
    estimate = payload["events"][0]["model_estimate"]
    assert estimate["source"] == "fallback"
    assert estimate["posterior_source"] == "statement"
    assert estimate["ready"] is False
    assert estimate["collecting"] is True
    assert estimate["predicted_good_or_easy_now"] is None
    assert estimate["prediction_status_now"] == "short-delay-excluded"
    assert 0.0 <= estimate["predicted_good_or_easy_at_due"] <= 1.0
    assert estimate["prediction_status_at_due"] == "available"
    interval_scale = estimate["posterior_interval_scale"]
    assert interval_scale["credible_interval_90"]["lower"] <= interval_scale["median"]
    assert interval_scale["median"] <= interval_scale["credible_interval_90"]["upper"]

    statistics = payload["statistics"]
    assert statistics["attempts"] == 3
    assert statistics["elapsed_ms"] == 240_000
    assert statistics["minutes"] == 4.0
    assert statistics["daily_timezone"] == "UTC"
    assert statistics["grades"] == {"again": 1, "hard": 0, "good": 2, "easy": 0}
    assert statistics["good_or_easy_self_grades"] == 2
    assert statistics["good_or_easy_self_grade_rate"] == pytest.approx(2 / 3)
    assert statistics["again_lapses"] == 1
    assert statistics["daily"][0]["attempts"] == 3
    assert all(bucket["attempts"] == 0 for bucket in statistics["daily"][1:])
    assert payload["calibration"]["processed_log_records"] == 3
    assert payload["calibration"]["target_grade"] == "good-or-easy"
    assert "weights" not in str(payload["calibration"])


def test_calendar_omits_disabled_and_orphaned_schedules_unless_requested(
    tmp_path, monkeypatch: pytest.MonkeyPatch
):
    current = datetime(2026, 9, 5, 12, 0, tzinfo=timezone.utc)
    monkeypatch.setattr(review_module, "_now", lambda: current)
    store = LibraryStore(tmp_path / "data")
    disabled_folder = store.create_folder("Disabled later", "disabled-later", None)
    deleted_folder = store.create_folder("Deleted entry", "deleted-entry", None)
    disabled_entry = store.create_entry(
        disabled_folder["id"], "df", "Disabled definition", "disabled", "", "Content"
    )
    deleted_entry = store.create_entry(
        deleted_folder["id"], "df", "Deleted definition", "deleted", "", "Content"
    )
    review = ReviewEngine(store)
    cards = {card["entry_id"]: card for card in review.queue()}
    for entry in (disabled_entry, deleted_entry):
        attempt = review.reveal(
            cards[entry["id"]]["id"],
            {"attempt": "Attempt", "confidence": 2, "elapsed_ms": 1_000, "overt": True},
        )
        review.grade(cards[entry["id"]]["id"], attempt["attempt_id"], 2)

    store.update_folder(disabled_folder["id"], {"review_enabled": False})
    store.delete_entry(deleted_entry["id"])
    start = current
    end = current + timedelta(days=10)

    assert review.calendar(start=start, end=end)["events"] == []
    payload = review.calendar(start=start, end=end, include_inactive=True)

    assert len(payload["events"]) == 2
    by_entry = {event["entry_id"]: event for event in payload["events"]}
    disabled = by_entry[disabled_entry["id"]]
    assert disabled["title"] == "Disabled definition"
    assert disabled["active"] is False
    assert disabled["review_enabled"] is False
    assert disabled["orphaned"] is False
    assert disabled["inactive_reason"] == "review-disabled"
    deleted = by_entry[deleted_entry["id"]]
    assert deleted["title"] is None
    assert deleted["canonical_tag"] is None
    assert deleted["active"] is False
    assert deleted["review_enabled"] is False
    assert deleted["orphaned"] is True
    assert deleted["inactive_reason"] == "entry-missing"
    assert payload["statistics"]["attempts"] == 2


def test_calendar_reports_again_as_a_fixed_ten_minute_retry(
    tmp_path, monkeypatch: pytest.MonkeyPatch
):
    current = datetime(2026, 9, 5, 12, 0, tzinfo=timezone.utc)
    monkeypatch.setattr(review_module, "_now", lambda: current)
    store = LibraryStore(tmp_path / "data")
    folder = store.create_folder("Foundations", "foundations", None)
    entry = store.create_entry(folder["id"], "df", "Set", "set", "", "Definition")
    review = ReviewEngine(store)
    card = next(card for card in review.queue() if card["entry_id"] == entry["id"])
    attempt = review.reveal(
        card["id"],
        {"attempt": "Attempt", "confidence": 2, "elapsed_ms": 1_000, "overt": True},
    )
    review.grade(card["id"], attempt["attempt_id"], 0)

    event = review.calendar(start=current, end=current + timedelta(hours=1))["events"][0]
    scheduler = event["schedule_at_last_grade"]["scheduler"]

    assert scheduler["reason"] == "again"
    assert scheduler["interval_days"] is None
    assert scheduler["interval_minutes"] == 10
    assert scheduler["calibrated_interval_used"] is False
    assert event["model_estimate"]["predicted_good_or_easy_at_due"] is None
    assert event["model_estimate"]["prediction_status_at_due"] == "short-delay-excluded"


def test_calendar_uses_half_open_aware_bounded_range_and_fails_closed_on_bad_log(
    settings_factory, monkeypatch: pytest.MonkeyPatch
):
    current = datetime(2026, 9, 5, 12, 0, tzinfo=timezone.utc)
    monkeypatch.setattr(review_module, "_now", lambda: current)
    app = create_app(settings_factory(), local_mode=True)
    folder = app.state.store.create_folder("Foundations", "foundations", None)
    app.state.store.create_entry(folder["id"], "df", "Set", "set", "", "Definition")

    with TestClient(
        app,
        base_url="http://127.0.0.1",
        client=("127.0.0.1", 50000),
    ) as client:
        card = client.get("/api/review/queue").json()["cards"][0]
        schedule = _grade(client, card["id"], 2, elapsed_ms=1_000)
        due_at = datetime.fromisoformat(str(schedule["due_at"]))

        excluded = client.get(
            "/api/review/calendar",
            params={"start": current.isoformat(), "end": due_at.isoformat()},
        )
        included = client.get(
            "/api/review/calendar",
            params={
                "start": due_at.isoformat(),
                "end": (due_at + timedelta(days=1)).isoformat(),
            },
        )
        naive = client.get(
            "/api/review/calendar",
            params={"start": "2026-09-05T00:00:00", "end": "2026-09-06T00:00:00Z"},
        )
        too_wide = client.get(
            "/api/review/calendar",
            params={
                "start": current.isoformat(),
                "end": (current + timedelta(days=367)).isoformat(),
            },
        )

        assert excluded.status_code == 200
        assert excluded.json()["events"] == []
        assert excluded.json()["statistics"]["attempts"] == 1
        assert included.status_code == 200
        assert [event["card_id"] for event in included.json()["events"]] == [card["id"]]
        assert included.json()["statistics"]["attempts"] == 0
        assert naive.status_code == 422
        assert "timezone" in naive.json()["detail"]
        assert too_wide.status_code == 422
        assert "366 days" in too_wide.json()["detail"]

        with app.state.review.log_path.open("a", encoding="utf-8") as stream:
            stream.write("not-json\n")
        malformed = client.get(
            "/api/review/calendar",
            params={
                "start": current.isoformat(),
                "end": (current + timedelta(days=10)).isoformat(),
            },
        )

    assert malformed.status_code == 422
    assert malformed.json()["detail"] == "review-log.jsonl is unreadable or invalid"


def test_calendar_daily_buckets_use_the_requested_iana_timezone(
    tmp_path, monkeypatch: pytest.MonkeyPatch
):
    current = datetime(2026, 9, 5, 0, 30, tzinfo=timezone.utc)
    monkeypatch.setattr(review_module, "_now", lambda: current)
    store = LibraryStore(tmp_path / "data")
    folder = store.create_folder("Foundations", "foundations", None)
    store.create_entry(folder["id"], "df", "Set", "set", "", "Definition")
    review = ReviewEngine(store)
    card = review.queue()[0]
    attempt = review.reveal(
        card["id"],
        {"attempt": "Attempt", "confidence": 2, "elapsed_ms": 60_000, "overt": True},
    )
    review.grade(card["id"], attempt["attempt_id"], 2)

    payload = review.calendar(
        start=current.replace(hour=0, minute=0),
        end=current.replace(hour=0, minute=0) + timedelta(days=1),
        timezone_name="America/Denver",
    )

    assert payload["statistics"]["daily_timezone"] == "America/Denver"
    assert [(bucket["date"], bucket["attempts"]) for bucket in payload["statistics"]["daily"]] == [
        ("2026-09-04", 1),
        ("2026-09-05", 0),
    ]
    with pytest.raises(StoreError, match="timezone is unknown"):
        review.calendar(
            start=current,
            end=current + timedelta(days=1),
            timezone_name="Mars/Olympus_Mons",
        )


def test_reporting_model_selects_ready_mode_then_ready_pool_and_reports_uncertainty():
    calibration = new_calibration_state()
    observed_at = datetime(2026, 1, 2, tzinfo=timezone.utc)
    previous = {
        "last_reviewed_at": (observed_at - timedelta(days=1)).isoformat(),
        "stability_days": 1.0,
    }
    for index in range(30):
        observe_review(
            calibration,
            "statement",
            previous,
            observed_at,
            2,
            card_id=f"statement-card-{index % 10}",
        )

    mode_estimate = reporting_model_estimate(
        calibration,
        "statement",
        delay_days_now=1.0,
        normalized_delay_now=0.5,
        delay_days_at_due=2.0,
        normalized_delay_at_due=1.0,
    )
    report = calibration_reporting_summary(calibration)

    assert mode_estimate["source"] == "statement"
    assert mode_estimate["posterior_source"] == "statement"
    assert mode_estimate["ready"] is True
    assert mode_estimate["collecting"] is False
    assert mode_estimate["predicted_good_or_easy_now"] > mode_estimate[
        "predicted_good_or_easy_at_due"
    ]
    statement = report["models"]["statement"]
    assert statement["ready"] is True
    assert statement["good_or_easy_self_grade_rate"] == 1.0
    assert statement["posterior_interval_scale"]["credible_interval_90"]["lower"] > 0

    pooled_only = new_calibration_state()
    for index in range(30):
        mode = "statement" if index % 2 == 0 else "solve"
        observe_review(
            pooled_only,
            mode,
            previous,
            observed_at,
            2,
            card_id=f"pooled-card-{index}",
        )
    pooled_estimate = reporting_model_estimate(
        pooled_only,
        "statement",
        delay_days_now=1.0,
        normalized_delay_now=0.5,
        delay_days_at_due=2.0,
        normalized_delay_at_due=1.0,
    )
    assert pooled_estimate["source"] == "pooled"
    assert pooled_estimate["posterior_source"] == "pooled"
    assert pooled_estimate["ready"] is True
