from __future__ import annotations

import json

import pytest
from fastapi.testclient import TestClient

from study_app.app import create_app
from study_app.review import ReviewEngine
from study_app.store import LibraryStore, StoreError


@pytest.mark.parametrize("version", [1, 2])
def test_entry_review_preserves_history_order_and_folder_inheritance(tmp_path, version):
    data = tmp_path / "data"
    if version == 1:
        data.mkdir()
        (data / "library.json").write_text('{"version":1,"folders":[],"entries":[]}')
    store = LibraryStore(data)
    parent = store.create_folder("Parent", "parent", None)
    child = store.create_folder("Child", "child", parent["id"])
    first, second = [
        store.create_entry(child["id"], "th", title, title.lower(), "", "Statement")
        for title in ("First", "Second")
    ]
    store.add_supplement(first["id"], {"kind": "pf", "label": "Proof", "content": "Proof"})
    review = ReviewEngine(store)
    card = review.queue()[0]
    attempt = review.reveal(card["id"], {"attempt": "Answer", "confidence": 2, "overt": True})
    review.grade(card["id"], attempt["attempt_id"], 2)
    pending = review.reveal(card["id"], {"attempt": "Answer", "confidence": 2, "overt": True})
    state_before = (data / "review.json").read_bytes()
    log_before = (data / "review-log.jsonl").read_bytes()
    all_cards = [c["id"] for c in review.queue(include_not_due=True)]
    assert len(all_cards) == 3  # Both theorem tasks plus the second statement.

    store.update_entry(first["id"], {"review_enabled": False})
    assert [c["entry_id"] for c in review.queue(include_not_due=True)] == [second["id"]]
    assert review.stats()["due"] == 1
    assert review.calendar()["events"] == []
    events = review.calendar(include_inactive=True)["events"]
    assert len(events) == 1 and events[0]["review_enabled"] is False
    assert [e["id"] for e in store.ordered_entries()] == [first["id"], second["id"]]
    assert LibraryStore(data).get_entry(first["id"])["review_enabled"] is False
    assert (data / "review.json").read_bytes() == state_before
    assert (data / "review-log.jsonl").read_bytes() == log_before
    assert pending["attempt_id"] in json.loads(state_before)["pending_attempts"]

    store.update_entry(first["id"], {"review_enabled": True})
    assert [c["id"] for c in review.queue(include_not_due=True)] == all_cards
    assert review.stats()["due"] == len(review.queue())
    store.update_folder(parent["id"], {"review_enabled": False})
    assert review.queue(include_not_due=True) == []
    assert review.stats()["due"] == 0
    store.update_folder(parent["id"], {"review_enabled": True})
    assert [c["id"] for c in review.queue(include_not_due=True)] == all_cards


@pytest.mark.parametrize("version", [1, 2])
def test_entry_preference_legacy_default_and_strict_disk_validation(tmp_path, version):
    data = tmp_path / "data"
    if version == 1:
        data.mkdir()
        (data / "library.json").write_text('{"version":1,"folders":[],"entries":[]}')
    store = LibraryStore(data)
    folder = store.create_folder("Folder", "folder", None)
    entry = store.create_entry(folder["id"], "df", "Item", "item", "", "Body")
    path = next(data.rglob("_entry.json")) if version == 2 else data / "library.json"
    value = json.loads(path.read_text())
    record = value if version == 2 else value["entries"][0]
    record.pop("review_enabled")
    path.write_text(json.dumps(value))
    before = path.read_bytes()
    fresh = LibraryStore(data)
    assert fresh.get_entry(entry["id"])["review_enabled"] is True
    assert len(ReviewEngine(fresh).queue()) == 1
    assert path.read_bytes() == before
    record["review_enabled"] = "false"
    path.write_text(json.dumps(value))
    with pytest.raises(StoreError, match="review_enabled must be true or false"):
        LibraryStore(data).check_data()


def test_entry_api_preference_response_and_single_sidecar_write(settings_factory):
    app = create_app(settings_factory(), local_mode=True)
    store = app.state.store
    folder = store.create_folder("Folder", "folder", None)
    headers = {"origin": "http://127.0.0.1", "x-study-csrf": "local"}
    with TestClient(app, base_url="http://127.0.0.1", client=("127.0.0.1", 50000)) as client:
        created = client.post("/api/entries", headers=headers, json={
            "folder_id": folder["id"], "kind": "df", "title": "Item", "tag": "item",
            "review_enabled": False,
        })
        assert created.status_code == 200
        entry = created.json()
        assert entry["review_enabled"] is False
        before = {p: p.read_bytes() for p in store.library_dir.rglob("*") if p.is_file()}
        url = f"/api/entries/{entry['id']}"
        updated = client.patch(url, params={"include_review_stats": True}, headers=headers,
                               json={"review_enabled": True})
        assert updated.status_code == 200
        assert updated.json()["entry"]["review_enabled"] is True
        assert updated.json()["review"]["due"] == 1
        changed = [p.name for p, content in before.items() if p.read_bytes() != content]
        assert changed == ["_entry.json"]
        legacy = client.patch(url, headers=headers, json={"review_enabled": False})
        assert legacy.json()["review_enabled"] is False
        assert "entry" not in legacy.json()
        invalid = client.patch(url, headers=headers, json={"review_enabled": "false"})
        assert invalid.status_code == 422
        assert client.get("/api/bootstrap?compact=true").json()["review"]["due"] == 0
