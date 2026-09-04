from __future__ import annotations

import json
import math
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

import study_app.review as review_module
from study_app.app import create_app
from study_app.review import ReviewEngine
from study_app.review_calibration import (
    HISTORY_DISCOUNT,
    TARGET_SUCCESS,
    calibration_summary,
    new_calibration_state,
    observe_review,
    posterior_predictive_success,
    schedule_interval,
    success_probability,
)
from study_app.store import LibraryStore, StoreError


def _previous(at: datetime, stability_days: float = 2.0) -> dict[str, object]:
    return {
        "last_reviewed_at": at.isoformat(),
        "stability_days": stability_days,
    }


def _add_observations(
    calibration: dict[str, object], *, grade: int, normalized_delay: float, count: int
) -> None:
    beginning = datetime(2026, 1, 1, tzinfo=timezone.utc)
    previous = _previous(beginning)
    for index in range(count):
        observed_at = beginning + timedelta(
            days=2.0 * normalized_delay, seconds=index
        )
        assert observe_review(
            calibration, "statement", previous, observed_at, grade
        ) is not None


def test_forgetting_curve_is_strict_and_neutral_scale_reaches_target():
    assert success_probability(0.0, 1.0) == pytest.approx(0.98)
    assert success_probability(1.0, 1.0) == pytest.approx(TARGET_SUCCESS)
    assert success_probability(2.0, 1.0) < success_probability(1.0, 1.0)
    assert success_probability(1000.0, 1.0) > 0.0


def test_calibration_falls_back_then_success_and_failure_move_intervals():
    calibration = new_calibration_state()
    interval, details = schedule_interval(calibration, "statement", 10.0, 1)
    assert interval == 10
    assert details["source"] == "fallback"
    assert details["calibrated"] is False

    _add_observations(calibration, grade=3, normalized_delay=1.0, count=30)
    longer, longer_details = schedule_interval(calibration, "statement", 10.0, 1)
    assert longer > 10
    assert longer_details["source"] == "statement"
    assert longer_details["calibrated"] is True

    failures = new_calibration_state()
    _add_observations(failures, grade=0, normalized_delay=1.0, count=30)
    shorter, shorter_details = schedule_interval(failures, "statement", 10.0, 1)
    assert shorter < 10
    assert shorter_details["calibrated"] is True


def test_the_observation_that_unlocks_calibration_only_changes_later_schedules():
    calibration = new_calibration_state()
    _add_observations(calibration, grade=3, normalized_delay=1.0, count=23)
    current_interval, current_details = schedule_interval(
        calibration, "statement", 10.0, 1
    )
    assert current_interval == 10
    assert current_details["source"] == "fallback"

    beginning = datetime(2026, 1, 1, tzinfo=timezone.utc)
    observe_review(
        calibration,
        "statement",
        _previous(beginning),
        beginning + timedelta(days=2),
        3,
    )
    later_interval, later_details = schedule_interval(calibration, "statement", 10.0, 1)
    assert later_interval > current_interval
    assert later_details["source"] == "statement"


def test_pooled_model_is_used_until_a_mode_has_enough_evidence():
    calibration = new_calibration_state()
    _add_observations(calibration, grade=3, normalized_delay=1.0, count=30)

    interval, details = schedule_interval(calibration, "solve", 10.0, 1)

    assert interval > 10
    assert details["source"] == "pooled"
    assert calibration_summary(calibration)["models"]["solve"]["observations"] == 0


def test_short_retries_and_first_reviews_do_not_train_the_model():
    calibration = new_calibration_state()
    reviewed_at = datetime(2026, 1, 1, tzinfo=timezone.utc)

    assert observe_review(calibration, "statement", {}, reviewed_at, 2) is None
    assert (
        observe_review(
            calibration,
            "statement",
            _previous(reviewed_at),
            reviewed_at + timedelta(hours=5, minutes=59),
            0,
        )
        is None
    )
    summary = calibration_summary(calibration)
    assert summary["models"]["pooled"]["observations"] == 0


def test_power_prior_slightly_discounts_old_observations():
    calibration = new_calibration_state()
    prior_prediction = posterior_predictive_success(
        calibration["models"]["statement"], 1.0
    )
    _add_observations(calibration, grade=2, normalized_delay=1.0, count=2)
    model = calibration["models"]["statement"]

    assert model["effective_observations"] == pytest.approx(1.0 + HISTORY_DISCOUNT)
    assert model["effective_observations"] < model["observations"]
    assert posterior_predictive_success(model, 1.0) > prior_prediction


def test_interrupted_state_write_recovers_one_calibration_observation(
    tmp_path, monkeypatch: pytest.MonkeyPatch
):
    current = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)
    monkeypatch.setattr(review_module, "_now", lambda: current)
    store = LibraryStore(tmp_path / "data")
    folder = store.create_folder("Foundations", "foundations", None)
    store.create_entry(folder["id"], "df", "Set", "set", "", "A collection")
    review = ReviewEngine(store)
    card = review.queue()[0]

    first_attempt = review.reveal(
        card["id"], {"attempt": "first", "confidence": 2, "overt": True}
    )
    review.grade(card["id"], first_attempt["attempt_id"], 2)

    current += timedelta(days=2)
    second_attempt = review.reveal(
        card["id"], {"attempt": "second", "confidence": 2, "overt": True}
    )
    original_write = review._write
    writes = 0

    def fail_once(state):
        nonlocal writes
        writes += 1
        if writes == 1:
            raise OSError("simulated interrupted state write")
        original_write(state)

    monkeypatch.setattr(review, "_write", fail_once)
    with pytest.raises(OSError, match="interrupted"):
        review.grade(card["id"], second_attempt["attempt_id"], 2)

    recovered = review.grade(card["id"], second_attempt["attempt_id"], 2)
    state = review._read()
    assert recovered["scheduler"]["source"] == "fallback"
    assert state["calibration"]["models"]["pooled"]["observations"] == 1
    assert state["calibration"]["models"]["statement"]["observations"] == 1
    records = [json.loads(line) for line in review.log_path.read_text().splitlines()]
    assert len(records) == 2
    assert records[-1]["calibration_observation"]["good_or_easy"] is True
    assert records[-1]["calibration_observation"]["normalized_delay"] == pytest.approx(1.0)


def test_reload_reconciles_logged_grade_without_retrying_original_request(
    tmp_path, monkeypatch: pytest.MonkeyPatch
):
    current = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)
    monkeypatch.setattr(review_module, "_now", lambda: current)
    store = LibraryStore(tmp_path / "data")
    folder = store.create_folder("Foundations", "foundations", None)
    store.create_entry(folder["id"], "df", "Set", "set", "", "A collection")
    review = ReviewEngine(store)
    card = review.queue()[0]

    first = review.reveal(
        card["id"], {"attempt": "first", "confidence": 2, "overt": True}
    )
    review.grade(card["id"], first["attempt_id"], 2)
    current += timedelta(days=2)
    interrupted = review.reveal(
        card["id"], {"attempt": "second", "confidence": 2, "overt": True}
    )

    def fail_write(_state):
        raise OSError("simulated interrupted state write")

    monkeypatch.setattr(review, "_write", fail_write)
    with pytest.raises(OSError, match="interrupted"):
        review.grade(card["id"], interrupted["attempt_id"], 2)

    replayed_observations = 0
    original_apply = review_module.apply_recorded_observation

    def count_apply(*args, **kwargs):
        nonlocal replayed_observations
        replayed_observations += 1
        return original_apply(*args, **kwargs)

    monkeypatch.setattr(review_module, "apply_recorded_observation", count_apply)
    reloaded = ReviewEngine(store)
    assert reloaded.queue() == []
    recovered = reloaded._read()
    assert recovered["cards"][card["id"]]["repetitions"] == 2
    assert recovered["pending_attempts"] == {}
    assert recovered["calibration"]["models"]["statement"]["observations"] == 1
    assert recovered["calibration"]["processed_log_records"] == 2
    assert replayed_observations == 1

    current += timedelta(days=5)
    next_attempt = reloaded.reveal(
        card["id"], {"attempt": "third", "confidence": 2, "overt": True}
    )
    reloaded.grade(card["id"], next_attempt["attempt_id"], 2)
    final_state = reloaded._read()
    assert final_state["cards"][card["id"]]["repetitions"] == 3
    assert final_state["calibration"]["models"]["statement"]["observations"] == 2
    assert len(reloaded.log_path.read_text(encoding="utf-8").splitlines()) == 3


def test_log_order_recovers_schedule_even_if_wall_clock_moves_backward(
    tmp_path, monkeypatch: pytest.MonkeyPatch
):
    current = datetime(2026, 1, 10, 12, 0, tzinfo=timezone.utc)
    monkeypatch.setattr(review_module, "_now", lambda: current)
    store = LibraryStore(tmp_path / "data")
    folder = store.create_folder("Foundations", "foundations", None)
    store.create_entry(folder["id"], "df", "Set", "set", "", "A collection")
    review = ReviewEngine(store)
    card = review.queue()[0]
    first = review.reveal(
        card["id"], {"attempt": "first", "confidence": 2, "overt": True}
    )
    review.grade(card["id"], first["attempt_id"], 2)
    first_reviewed_at = current.isoformat()

    current -= timedelta(days=1)
    second = review.reveal(
        card["id"], {"attempt": "second", "confidence": 2, "overt": True}
    )

    def fail_write(_state):
        raise OSError("simulated interrupted state write")

    monkeypatch.setattr(review, "_write", fail_write)
    with pytest.raises(OSError, match="interrupted"):
        review.grade(card["id"], second["attempt_id"], 2)

    restarted = ReviewEngine(store)
    restarted.queue(include_not_due=True)
    recovered = restarted._read()
    assert recovered["cards"][card["id"]]["repetitions"] == 2
    assert recovered["cards"][card["id"]]["last_reviewed_at"] == first_reviewed_at
    assert recovered["pending_attempts"] == {}


def test_grade_never_schedules_before_retrieval_when_clock_rolls_back(
    tmp_path, monkeypatch: pytest.MonkeyPatch
):
    current = datetime(2026, 1, 10, 12, 0, tzinfo=timezone.utc)
    monkeypatch.setattr(review_module, "_now", lambda: current)
    store = LibraryStore(tmp_path / "data")
    folder = store.create_folder("Foundations", "foundations", None)
    store.create_entry(folder["id"], "df", "Set", "set", "", "A collection")
    review = ReviewEngine(store)
    card = review.queue()[0]
    attempt = review.reveal(
        card["id"], {"attempt": "first", "confidence": 2, "overt": True}
    )
    retrieval_at = current

    current -= timedelta(days=1)
    scheduled = review.grade(card["id"], attempt["attempt_id"], 2)

    assert scheduled["last_reviewed_at"] == retrieval_at.isoformat()
    assert scheduled["due_at"] == (retrieval_at + timedelta(days=2)).isoformat()
    record = json.loads(review.log_path.read_text(encoding="utf-8"))
    assert record["graded_at"] == current.isoformat()
    assert record["schedule"]["last_reviewed_at"] == retrieval_at.isoformat()
    assert review.validate_log()["processed_log_records"] == 1


def test_log_validation_rejects_a_card_moving_backward_between_records(
    tmp_path, monkeypatch: pytest.MonkeyPatch
):
    current = datetime(2026, 1, 10, 12, 0, tzinfo=timezone.utc)
    monkeypatch.setattr(review_module, "_now", lambda: current)
    store = LibraryStore(tmp_path / "data")
    folder = store.create_folder("Foundations", "foundations", None)
    store.create_entry(folder["id"], "df", "Set", "set", "", "A collection")
    review = ReviewEngine(store)
    card = review.queue()[0]

    for label in ("first", "second"):
        attempt = review.reveal(
            card["id"], {"attempt": label, "confidence": 2, "overt": True}
        )
        review.grade(card["id"], attempt["attempt_id"], 2)
        current += timedelta(days=2)

    records = [json.loads(line) for line in review.log_path.read_text().splitlines()]
    reversed_at = datetime(2026, 1, 5, 12, 0, tzinfo=timezone.utc)
    records[1]["started_at"] = reversed_at.isoformat()
    records[1]["graded_at"] = reversed_at.isoformat()
    records[1]["schedule"]["last_reviewed_at"] = reversed_at.isoformat()
    records[1]["schedule"]["due_at"] = (reversed_at + timedelta(days=1)).isoformat()
    review.log_path.write_text(
        "".join(json.dumps(record) + "\n" for record in records),
        encoding="utf-8",
    )

    with pytest.raises(StoreError, match="moves its card backward in time"):
        ReviewEngine(store).validate_log()


def test_explicit_observation_survives_rebuild_when_earlier_log_is_missing(
    tmp_path, monkeypatch: pytest.MonkeyPatch
):
    current = datetime(2026, 1, 3, 12, 0, tzinfo=timezone.utc)
    monkeypatch.setattr(review_module, "_now", lambda: current)
    store = LibraryStore(tmp_path / "data")
    folder = store.create_folder("Foundations", "foundations", None)
    store.create_entry(folder["id"], "df", "Set", "set", "", "A collection")
    review = ReviewEngine(store)
    card = review.queue()[0]
    state = review._read()
    state["cards"][card["id"]] = {
        "due_at": current.isoformat(),
        "last_reviewed_at": (current - timedelta(days=2)).isoformat(),
        "last_grade": 2,
        "last_elapsed_ms": 0,
        "stability_days": 2.0,
        "difficulty": 5.0,
        "repetitions": 1,
        "lapses": 0,
        "last_confidence": 2,
        "last_calibration": 0,
    }
    review._write(state)

    first = review.reveal(
        card["id"], {"attempt": "first logged", "confidence": 2, "overt": True}
    )
    review.grade(card["id"], first["attempt_id"], 2)
    rebuilt = review._read()
    rebuilt.pop("calibration")
    review._write(rebuilt)

    assert review.validate_log()["models"]["statement"]["observations"] == 1
    current += timedelta(days=5)
    second = review.reveal(
        card["id"], {"attempt": "second logged", "confidence": 2, "overt": True}
    )
    review.grade(card["id"], second["attempt_id"], 2)
    assert review._read()["calibration"]["models"]["statement"]["observations"] == 2


def test_semantic_log_validation_rejects_incomplete_records(tmp_path):
    store = LibraryStore(tmp_path / "data")
    review = ReviewEngine(store)
    review.log_path.write_text(
        json.dumps({"id": "a" * 32, "card_id": "entry::statement"}) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(StoreError, match="does not match its card"):
        review.validate_log()


def test_new_engine_rebuilds_a_tampered_but_well_formed_calibration_cache(
    tmp_path, monkeypatch: pytest.MonkeyPatch
):
    current = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)
    monkeypatch.setattr(review_module, "_now", lambda: current)
    store = LibraryStore(tmp_path / "data")
    folder = store.create_folder("Foundations", "foundations", None)
    store.create_entry(folder["id"], "df", "Set", "set", "", "A collection")
    review = ReviewEngine(store)
    card = review.queue()[0]
    attempt = review.reveal(
        card["id"], {"attempt": "first", "confidence": 2, "overt": True}
    )
    review.grade(card["id"], attempt["attempt_id"], 2)

    state = review._read()
    state["calibration"]["models"]["statement"].update(
        {
            "observations": 1,
            "successes": 1,
            "effective_observations": 1.0,
            "effective_successes": 1.0,
            "effective_exposure": 1.0,
            "last_observed_at": current.isoformat(),
        }
    )
    review._write(state)

    restarted = ReviewEngine(store)
    restarted.queue(include_not_due=True)
    repaired = restarted._read()["calibration"]["models"]["statement"]
    assert repaired["observations"] == 0
    assert repaired["effective_observations"] == 0.0

    same_process = restarted._read()
    same_process["calibration"]["models"]["statement"].update(
        {
            "observations": 1,
            "successes": 1,
            "effective_observations": 1.0,
            "effective_successes": 1.0,
            "effective_exposure": 1.0,
            "last_observed_at": current.isoformat(),
        }
    )
    restarted._write(same_process)
    restarted.queue(include_not_due=True)
    repaired_again = restarted._read()["calibration"]["models"]["statement"]
    assert repaired_again["observations"] == 0


def test_same_engine_repairs_a_tampered_card_schedule_from_the_log(
    tmp_path, monkeypatch: pytest.MonkeyPatch
):
    current = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)
    monkeypatch.setattr(review_module, "_now", lambda: current)
    store = LibraryStore(tmp_path / "data")
    folder = store.create_folder("Foundations", "foundations", None)
    store.create_entry(folder["id"], "df", "Set", "set", "", "A collection")
    review = ReviewEngine(store)
    card = review.queue()[0]
    attempt = review.reveal(
        card["id"], {"attempt": "first", "confidence": 2, "overt": True}
    )
    review.grade(card["id"], attempt["attempt_id"], 2)

    tampered = review._read()
    tampered["cards"][card["id"]]["stability_days"] = 1000.0
    review._write(tampered)
    review.queue(include_not_due=True)

    repaired = review._read()
    assert repaired["cards"][card["id"]]["stability_days"] == 2.0


def test_verified_restart_and_forced_rebuild_do_not_rewrite_unchanged_state(
    tmp_path, monkeypatch: pytest.MonkeyPatch
):
    current = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)
    monkeypatch.setattr(review_module, "_now", lambda: current)
    store = LibraryStore(tmp_path / "data")
    folder = store.create_folder("Foundations", "foundations", None)
    store.create_entry(folder["id"], "df", "Set", "set", "", "A collection")
    review = ReviewEngine(store)
    card = review.queue()[0]
    attempt = review.reveal(
        card["id"], {"attempt": "first", "confidence": 2, "overt": True}
    )
    review.grade(card["id"], attempt["attempt_id"], 2)
    before = review.state_path.read_bytes()

    restarted = ReviewEngine(store)
    restarted.queue(include_not_due=True)
    assert restarted.state_path.read_bytes() == before

    restarted.rebuild_calibration()
    assert restarted.state_path.read_bytes() == before

    validated_records = 0
    original_validate = restarted._validate_log_record

    def count_validation(value, line_number):
        nonlocal validated_records
        validated_records += 1
        return original_validate(value, line_number)

    monkeypatch.setattr(restarted, "_validate_log_record", count_validation)
    cached_attempt = restarted.reveal(
        card["id"], {"attempt": "cached", "confidence": 2, "overt": True}
    )
    saved = restarted.grade(card["id"], cached_attempt["attempt_id"], 2)
    repeated = restarted.grade(card["id"], cached_attempt["attempt_id"], 2)
    restarted.queue(include_not_due=True)

    assert repeated["due_at"] == saved["due_at"]
    assert validated_records == 0


def test_append_repairs_a_valid_log_without_a_final_newline(
    tmp_path, monkeypatch: pytest.MonkeyPatch
):
    current = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)
    monkeypatch.setattr(review_module, "_now", lambda: current)
    store = LibraryStore(tmp_path / "data")
    folder = store.create_folder("Foundations", "foundations", None)
    store.create_entry(folder["id"], "df", "Set", "set", "", "A collection")
    review = ReviewEngine(store)
    card = review.queue()[0]
    first = review.reveal(
        card["id"], {"attempt": "first", "confidence": 2, "overt": True}
    )
    review.grade(card["id"], first["attempt_id"], 2)
    review.log_path.write_bytes(review.log_path.read_bytes().rstrip(b"\n"))

    current += timedelta(days=5)
    restarted = ReviewEngine(store)
    restarted.queue(include_not_due=True)
    second = restarted.reveal(
        card["id"], {"attempt": "second", "confidence": 2, "overt": True}
    )
    restarted.grade(card["id"], second["attempt_id"], 2)

    assert len(restarted.log_path.read_text(encoding="utf-8").splitlines()) == 2
    assert ReviewEngine(store).validate_log()["processed_log_records"] == 2


def test_mixed_live_updates_match_authoritative_full_replay(
    tmp_path, monkeypatch: pytest.MonkeyPatch
):
    current = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)
    monkeypatch.setattr(review_module, "_now", lambda: current)
    store = LibraryStore(tmp_path / "data")
    folder = store.create_folder("Mathematics", "mathematics", None)
    store.create_entry(folder["id"], "df", "Set", "set", "", "Definition")
    theorem = store.create_entry(
        folder["id"], "th", "Small theorem", "small-theorem", "", "Statement"
    )
    store.add_supplement(
        theorem["id"],
        {"kind": "pf", "label": "Proof", "content": "Proof", "main": True},
    )
    problem = store.create_entry(
        folder["id"], "pb", "Small problem", "small-problem", "", "Problem"
    )
    store.add_supplement(
        problem["id"],
        {"kind": "sl", "label": "Solution", "content": "Solution", "main": True},
    )
    review = ReviewEngine(store)
    cards = {
        card["mode"]: card for card in review.queue(include_not_due=True)
    }
    modes = ("statement", "proof-plan", "solve")
    grades = (2, 3, 1, 2, 0, 3)

    for index in range(36):
        current += timedelta(days=2 + index % 4)
        card = cards[modes[index % len(modes)]]
        attempt = review.reveal(
            card["id"],
            {"attempt": f"attempt {index}", "confidence": 2, "overt": True},
        )
        review.grade(card["id"], attempt["attempt_id"], grades[index % len(grades)])

    live = review._read()["calibration"]
    live_interval = schedule_interval(live, "statement", 10.0, 1)
    review.rebuild_calibration()
    replayed = review._read()["calibration"]
    replayed_interval = schedule_interval(replayed, "statement", 10.0, 1)

    assert replayed["processed_log_records"] == 36
    assert replayed == live
    assert replayed_interval == live_interval


@pytest.mark.parametrize("stability", [math.nan, math.inf, -math.inf, 10**400])
def test_interval_scheduler_rejects_nonfinite_stability(stability):
    with pytest.raises(ValueError, match="stability"):
        schedule_interval(new_calibration_state(), "statement", stability, 1)


def test_interval_scheduler_caps_huge_finite_stability_before_rounding():
    interval, details = schedule_interval(
        new_calibration_state(), "statement", 1e308, 1
    )

    assert interval == 3650
    assert details["interval_days"] == 3650


def test_review_api_preserves_queue_reveal_grade_contract(settings_factory):
    app = create_app(settings_factory(), local_mode=True)
    folder = app.state.store.create_folder("Foundations", "foundations", None)
    app.state.store.create_entry(
        folder["id"], "df", "Set", "set", "", "A collection of objects"
    )
    headers = {"origin": "http://127.0.0.1", "x-study-csrf": "local"}

    with TestClient(
        app,
        base_url="http://127.0.0.1",
        client=("127.0.0.1", 50000),
    ) as client:
        calibration = client.get("/api/bootstrap").json()["review"]["calibration"]
        assert calibration["target_grade"] == "good-or-easy"
        assert calibration["models"]["pooled"]["ready"] is False
        card = client.get("/api/review/queue").json()["cards"][0]
        revealed = client.post(
            f"/api/review/{card['id']}/reveal",
            json={"attempt": "A collection", "confidence": 2, "overt": True},
            headers=headers,
        )
        assert revealed.status_code == 200
        graded = client.post(
            f"/api/review/{card['id']}/grade",
            json={"attempt_id": revealed.json()["attempt_id"], "grade": 2},
            headers=headers,
        )

    assert graded.status_code == 200
    payload = graded.json()
    assert datetime.fromisoformat(payload["due_at"])
    assert payload["retry_in_session"] is False
    assert payload["retry_after_items"] is None
    assert payload["scheduler"]["model"] == "discounted-bayesian-retention-v1"
    assert payload["scheduler"]["source"] == "fallback"
