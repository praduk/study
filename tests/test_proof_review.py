from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import study_app.review as review_module
from study_app.app import create_app
from study_app.review import ReviewEngine
from study_app.store import LibraryStore, StoreError


def _store(data: Path, version: int) -> LibraryStore:
    if version == 1:
        data.mkdir()
        (data / "library.json").write_text('{"version":1,"folders":[],"entries":[]}')
    return LibraryStore(data)


def _theorem(store: LibraryStore, folder_id: str, title: str = "Result") -> dict:
    entry = store.create_entry(folder_id, "th", title, title.lower(), "", "Statement")
    return store.add_supplement(
        entry["id"], {"kind": "pf", "label": "Proof", "content": "Complete proof"}
    )


def _attempt() -> dict:
    return {"attempt": "My proof", "confidence": 2, "elapsed_ms": 1_000, "overt": True}


@pytest.mark.parametrize("version", [1, 2])
def test_proof_opt_out_preserves_capability_content_and_review_history(tmp_path, monkeypatch, version):
    current = datetime(2026, 10, 30, 12, tzinfo=timezone.utc)
    monkeypatch.setattr(review_module, "_now", lambda: current)
    data = tmp_path / "data"
    store = _store(data, version)
    folder = store.create_folder("Algebra", "algebra", None)
    first = _theorem(store, folder["id"], "First")
    second = _theorem(store, folder["id"], "Second")
    review = ReviewEngine(store)
    all_ids = [card["id"] for card in review.queue()]
    proof_id = f"{first['id']}::proof-plan"
    assert all_ids == [
        f"{first['id']}::statement", proof_id,
        f"{second['id']}::statement", f"{second['id']}::proof-plan",
    ]

    completed = review.reveal(proof_id, _attempt())
    schedule = review.grade(proof_id, completed["attempt_id"], 0)
    assert schedule["retry_in_session"] is True
    assert datetime.fromisoformat(schedule["due_at"]) == current + timedelta(minutes=10)
    pending = review.reveal(proof_id, _attempt())
    current += timedelta(minutes=11)
    assert [card["id"] for card in review.queue()] == all_ids
    state_before = review.state_path.read_bytes()
    log_before = review.log_path.read_bytes()
    stored_schedule = json.loads(state_before)["cards"][proof_id]
    proof_before = store.get_entry(first["id"])["supplements"]

    store.update_entry(first["id"], {"proof_review_enabled": False})
    # Reopening exercises persistence and prevents an in-memory cache from
    # disguising a missing sidecar/aggregate preference.
    store = LibraryStore(data)
    review = ReviewEngine(store)
    disabled = store.get_entry(first["id"])
    assert disabled["proof_review_enabled"] is False
    assert disabled["review_modes"] == ["statement", "proof-plan"]
    assert disabled["supplements"] == proof_before
    assert store.review_mode_available(disabled, "proof-plan") is True
    assert [card["id"] for card in review.queue(include_not_due=True)] == [
        card_id for card_id in all_ids if card_id != proof_id
    ]
    assert review.stats()["due"] == 3
    assert review.calendar()["events"] == []
    report = review.calendar(include_inactive=True)
    assert report["statistics"]["attempts"] == 1
    event, = report["events"]
    assert event["card_id"] == proof_id
    assert event["active"] is False
    assert event["review_enabled"] is True
    assert event["orphaned"] is False
    assert event["inactive_reason"] == "proof-review-disabled"
    assert event["schedule_at_last_grade"] == stored_schedule

    # A card already loaded in a browser cannot reveal another proof while
    # disabled. A retry of an already committed grade stays idempotent.
    with pytest.raises(StoreError, match="(not enabled|disabled)"):
        review.reveal(proof_id, _attempt())
    assert review.grade(proof_id, completed["attempt_id"], 0)["due_at"] == schedule["due_at"]
    assert review.state_path.read_bytes() == state_before
    assert review.log_path.read_bytes() == log_before
    assert pending["attempt_id"] in json.loads(state_before)["pending_attempts"]

    store.update_entry(first["id"], {"proof_review_enabled": True})
    restored = review.queue()
    assert [card["id"] for card in restored] == all_ids
    assert next(card for card in restored if card["id"] == proof_id)["due_at"] == schedule["due_at"]
    assert review.stats()["due"] == 4
    assert review.calendar()["events"][0]["inactive_reason"] is None
    assert review.state_path.read_bytes() == state_before
    assert review.log_path.read_bytes() == log_before
    # As with entry/folder opt-out, an attempt already revealed may still be
    # completed. This is an explicit new grade, not a consequence of toggling.
    store.update_entry(first["id"], {"proof_review_enabled": False})
    review.grade(proof_id, pending["attempt_id"], 2)
    assert review.validate_log()["processed_log_records"] == 2
    assert proof_id not in {card["id"] for card in review.queue(include_not_due=True)}


@pytest.mark.parametrize("master", ["entry", "ancestor"])
def test_proof_preference_remains_subordinate_to_master_review_preferences(tmp_path, master):
    store = LibraryStore(tmp_path / "data")
    parent = store.create_folder("Parent", "parent", None)
    child = store.create_folder("Child", "child", parent["id"])
    entry = _theorem(store, child["id"])
    review = ReviewEngine(store)
    proof_id = f"{entry['id']}::proof-plan"
    attempt = review.reveal(proof_id, _attempt())
    review.grade(proof_id, attempt["attempt_id"], 2)
    def update_master(enabled):
        if master == "entry":
            store.update_entry(entry["id"], {"review_enabled": enabled})
        else:
            store.update_folder(parent["id"], {"review_enabled": enabled})

    update_master(False)
    for enabled in (False, True, False):
        store.update_entry(entry["id"], {"proof_review_enabled": enabled})
        assert review.queue(include_not_due=True) == []
        assert review.stats()["due"] == 0
        assert review.calendar()["events"] == []
        event, = review.calendar(include_inactive=True)["events"]
        assert event["inactive_reason"] == "review-disabled"

    update_master(True)
    assert [card["mode"] for card in review.queue(include_not_due=True)] == ["statement"]
    assert review.stats()["due"] == 1
    store.update_entry(entry["id"], {"proof_review_enabled": True})
    assert [card["mode"] for card in review.queue(include_not_due=True)] == [
        "statement", "proof-plan"
    ]


@pytest.mark.parametrize("version", [1, 2])
def test_legacy_theorem_defaults_to_proof_review_without_rewriting_authored_data(tmp_path, version):
    data = tmp_path / "data"
    store = _store(data, version)
    folder = store.create_folder("Algebra", "algebra", None)
    entry = _theorem(store, folder["id"])
    path = next(data.rglob("_entry.json")) if version == 2 else data / "library.json"
    value = json.loads(path.read_text())
    record = value if version == 2 else value["entries"][0]
    record.pop("proof_review_enabled", None)
    path.write_text(json.dumps(value))
    before = path.read_bytes()

    reopened = LibraryStore(data)
    assert reopened.get_entry(entry["id"])["proof_review_enabled"] is True
    assert [card["mode"] for card in ReviewEngine(reopened).queue()] == [
        "statement", "proof-plan"
    ]
    reopened.check_data()
    assert path.read_bytes() == before


@pytest.mark.parametrize("kind", ["ax", "df", "rk", "pb"])
def test_proof_preference_does_not_disable_other_entry_kinds(tmp_path, kind):
    store = LibraryStore(tmp_path / "data")
    folder = store.create_folder("Folder", "folder", None)
    entry = store.create_entry(
        folder["id"], kind, "Item", "item", "", "Body", proof_review_enabled=False
    )
    if kind == "pb":
        store.add_supplement(entry["id"], {"kind": "sl", "label": "Solution", "content": "Answer"})
    expected = "solve" if kind == "pb" else "statement"
    assert [card["mode"] for card in ReviewEngine(store).queue()] == [expected]


def test_proof_preference_api_preserves_content_and_accepts_later_proof(settings_factory):
    app = create_app(settings_factory(), local_mode=True)
    store = app.state.store
    folder = store.create_folder("Algebra", "algebra", None)
    headers = {"origin": "http://127.0.0.1", "x-study-csrf": "local"}
    with TestClient(app, base_url="http://127.0.0.1", client=("127.0.0.1", 50000)) as client:
        created = client.post("/api/entries", headers=headers, json={
            "folder_id": folder["id"], "kind": "th", "title": "Result", "tag": "result",
            "content": "Statement", "proof_review_enabled": False,
        })
        assert created.status_code == 200
        entry = created.json()
        assert entry["proof_review_enabled"] is False
        assert entry["review_modes"] == ["statement"]
        added = store.add_supplement(entry["id"], {
            "kind": "pf", "label": "Proof", "content": "A complete proof",
        })
        assert added["proof_review_enabled"] is False
        assert added["review_modes"] == ["statement", "proof-plan"]
        assert [card["mode"] for card in client.get("/api/review/queue").json()["cards"]] == [
            "statement"
        ]

        before = {path: path.read_bytes() for path in store.library_dir.rglob("*") if path.is_file()}
        url = f"/api/entries/{entry['id']}"
        enabled = client.patch(url, params={"include_review_stats": True}, headers=headers,
                               json={"proof_review_enabled": True})
        assert enabled.status_code == 200
        assert enabled.json()["entry"]["proof_review_enabled"] is True
        assert enabled.json()["review"]["due"] == 2
        changed = [path.name for path, content in before.items() if path.read_bytes() != content]
        assert changed == ["_entry.json"]

        proof_id = f"{entry['id']}::proof-plan"
        revealed = client.post(f"/api/review/{proof_id}/reveal", headers=headers, json=_attempt())
        assert revealed.status_code == 200
        assert revealed.json()["answer"]["primary"]["content"] == "A complete proof\n"
        disabled = client.patch(url, headers=headers, json={"proof_review_enabled": False})
        assert disabled.status_code == 200
        assert disabled.json()["proof_review_enabled"] is False
        assert "entry" not in disabled.json()
        assert client.post(f"/api/review/{proof_id}/reveal", headers=headers,
                           json=_attempt()).status_code == 422
        assert client.post(f"/api/review/{proof_id}/grade", headers=headers, json={
            "attempt_id": revealed.json()["attempt_id"], "grade": 2,
        }).status_code == 200
        statement = client.post(f"/api/review/{entry['id']}::statement/reveal", headers=headers,
                                json=_attempt())
        assert statement.status_code == 200
        assert statement.json()["answer"]["primary"]["content"] == "Statement\n"
        assert client.get("/api/bootstrap?compact=true").json()["review"]["due"] == 1
        assert store.get_entry(entry["id"])["supplements"] == added["supplements"]
        unchanged = client.patch(url, headers=headers, json={"proof_review_enabled": None})
        assert unchanged.status_code == 200
        assert unchanged.json()["proof_review_enabled"] is False


@pytest.mark.parametrize("invalid", [0, 1, "false", "true", [], {}])
def test_proof_preference_api_requires_boolean(settings_factory, invalid):
    app = create_app(settings_factory(), local_mode=True)
    store = app.state.store
    folder = store.create_folder("Folder", "folder", None)
    entry = _theorem(store, folder["id"])
    headers = {"origin": "http://127.0.0.1", "x-study-csrf": "local"}
    with TestClient(app, base_url="http://127.0.0.1", client=("127.0.0.1", 50000)) as client:
        created = client.post("/api/entries", headers=headers, json={
            "folder_id": folder["id"], "kind": "th", "title": "Other", "tag": "other",
            "proof_review_enabled": invalid,
        })
        assert created.status_code == 422
        updated = client.patch(f"/api/entries/{entry['id']}", headers=headers,
                               json={"proof_review_enabled": invalid})
        assert updated.status_code == 422
        assert store.get_entry(entry["id"])["proof_review_enabled"] is True
        assert len(store.snapshot()["entries"]) == 1
