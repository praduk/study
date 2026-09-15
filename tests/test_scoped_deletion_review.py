from __future__ import annotations

import json
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

import study_app.review as review_module
from study_app.app import create_app
from study_app.review import ReviewEngine
from study_app.store import LibraryStore, StoreError


@pytest.fixture
def reviewed_library(settings_factory, monkeypatch: pytest.MonkeyPatch):
    clock = {"now": datetime(2026, 9, 14, 12, tzinfo=timezone.utc)}
    monkeypatch.setattr(review_module, "_now", lambda: clock["now"])
    settings = settings_factory()
    app = create_app(settings, local_mode=True)
    store: LibraryStore = app.state.store
    review: ReviewEngine = app.state.review
    folder = store.create_folder("Algebra", "algebra", None)
    entries = [
        store.create_entry(folder["id"], "df", title, title.lower(), "", f"{title} body")
        for title in ("Group", "Ring", "Field")
    ]
    for _ in range(2):
        for entry in entries:
            card_id = review.card_id(entry["id"], "statement")
            attempt = review.reveal(card_id, {
                "attempt": "A test response", "confidence": 2, "overt": True,
                "elapsed_ms": 1_000,
            })
            review.grade(card_id, attempt["attempt_id"], 2)
        clock["now"] += timedelta(days=2)
    for entry in (entries[0], entries[2]):
        review.reveal(review.card_id(entry["id"], "statement"), {
            "attempt": "Pending test response", "confidence": 2, "overt": True,
            "elapsed_ms": 500,
        })
    review.queue(include_not_due=True)
    return settings, store, review, entries


def _pending_entry_ids(store: LibraryStore) -> set[str]:
    return {entry_id for entry_ids in store.pending_deletions().values() for entry_id in entry_ids}


def _log_records(review: ReviewEngine):
    return [json.loads(line) for line in review.log_path.read_text().splitlines() if line.strip()]


def _assert_cleanup(
    review: ReviewEngine, before_state: dict, deleted_ids: set[str], surviving_ids: set[str]
):
    state = review._read()
    assert all(card_id.split("::")[0] not in deleted_ids for card_id in state["cards"])
    assert all(attempt["entry_id"] not in deleted_ids
               for attempt in state["pending_attempts"].values())
    assert all(record["entry_id"] not in deleted_ids for record in _log_records(review))
    for card_id, card in before_state["cards"].items():
        if card_id.split("::")[0] in surviving_ids:
            assert state["cards"][card_id] == card
    for attempt_id, attempt in before_state["pending_attempts"].items():
        if attempt["entry_id"] in surviving_ids:
            assert state["pending_attempts"][attempt_id] == attempt
    assert not review.store.pending_deletions()
    assert review.validate_log()["processed_log_records"] == 2 * len(surviving_ids)


def _save_entry_directory(store: LibraryStore, entry: dict, destination: Path) -> Path:
    source = (store.data_dir / entry["formulations"][0]["file"]).parent
    shutil.copytree(source, destination)
    return source


def test_startup_finishes_committed_deletion_before_review_cleanup(reviewed_library):
    settings, store, review, entries = reviewed_library
    before_state = review._read()
    state_bytes = review.state_path.read_bytes()
    log_bytes = review.log_path.read_bytes()
    deleted_id = entries[0]["id"]
    store.delete_entry(deleted_id)

    assert _pending_entry_ids(store) == {deleted_id}
    assert review.state_path.read_bytes() == state_bytes
    assert review.log_path.read_bytes() == log_bytes
    restarted = create_app(settings, local_mode=True)
    _assert_cleanup(restarted.state.review, before_state, {deleted_id},
                    {entry["id"] for entry in entries[1:]})
    assert deleted_id not in {
        entry["id"] for entry in restarted.state.store.snapshot(include_tree=False)["entries"]
    }


@pytest.mark.parametrize("failure_point", ["log", "state"])
def test_interrupted_review_compaction_keeps_deletion_pending_until_restart(
    reviewed_library, monkeypatch: pytest.MonkeyPatch, failure_point: str
):
    settings, store, review, entries = reviewed_library
    before_state = review._read()
    state_bytes = review.state_path.read_bytes()
    log_bytes = review.log_path.read_bytes()
    deleted_id = entries[0]["id"]
    store.delete_entry(deleted_id)
    original_atomic = review_module._atomic_bytes

    def fail_log_write(path, value):
        if path == review.log_path:
            raise StoreError("injected review log failure")
        return original_atomic(path, value)

    def fail_state_write(state):
        raise StoreError("injected review state failure")

    with monkeypatch.context() as patch:
        if failure_point == "log":
            patch.setattr(review_module, "_atomic_bytes", fail_log_write)
        else:
            patch.setattr(review, "_write", fail_state_write)
        with pytest.raises(StoreError, match="injected review"):
            review.prune_to_current_library()
    assert _pending_entry_ids(store) == {deleted_id}
    assert review.state_path.read_bytes() == state_bytes
    if failure_point == "log":
        assert review.log_path.read_bytes() == log_bytes
    else:
        assert all(record["entry_id"] != deleted_id for record in _log_records(review))
    restarted = create_app(settings, local_mode=True)
    _assert_cleanup(restarted.state.review, before_state, {deleted_id},
                    {entry["id"] for entry in entries[1:]})


def test_restored_entry_id_does_not_restore_deleted_review_history(
    reviewed_library, tmp_path: Path
):
    _settings, store, review, entries = reviewed_library
    target = entries[0]
    before_state = review._read()
    saved = tmp_path / "saved-entry"
    original_path = _save_entry_directory(store, target, saved)
    store.delete_entry(target["id"])
    shutil.copytree(saved, original_path)

    # The complete card-ID set matches the previous queue again. The durable
    # deletion intent must still trigger pruning before this restored card runs.
    cards = review.queue(include_not_due=True)
    restored = next(card for card in cards if card["entry_id"] == target["id"])
    assert restored["new"] is True
    assert store.get_entry(target["id"])["title"] == target["title"]
    _assert_cleanup(review, before_state, {target["id"]},
                    {entry["id"] for entry in entries[1:]})


def test_ack_failure_blocks_restored_id_attempt_until_cleanup_is_durable(
    reviewed_library, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    _settings, store, review, entries = reviewed_library
    target = entries[0]
    saved = tmp_path / "saved-entry"
    original_path = _save_entry_directory(store, target, saved)
    store.delete_entry(target["id"])
    shutil.copytree(saved, original_path)
    card_id = review.card_id(target["id"], "statement")
    payload = {"attempt": "A new test response", "confidence": 2, "overt": True}

    def fail_ack(transaction_ids):
        raise StoreError("injected deletion acknowledgment failure")

    with monkeypatch.context() as patch:
        patch.setattr(store, "complete_pending_deletions", fail_ack)
        with pytest.raises(StoreError, match="acknowledgment"):
            review.reveal(card_id, payload)
        assert _pending_entry_ids(store) == {target["id"]}
        assert all(attempt["entry_id"] != target["id"]
                   for attempt in review._read()["pending_attempts"].values())
        with pytest.raises(StoreError, match="acknowledgment"):
            review.reveal(card_id, payload)

    attempt = review.reveal(card_id, payload)
    schedule = review.grade(card_id, attempt["attempt_id"], 2)
    assert schedule["repetitions"] == 1
    assert not store.pending_deletions()
    # A review-complete trash directory may remain awaiting background removal;
    # it must not make later pruning erase this new attempt for the restored ID.
    review.prune_to_current_library()
    assert sum(record["entry_id"] == target["id"] for record in _log_records(review)) == 1


def test_visible_ack_with_failed_directory_fsync_blocks_new_review(
    reviewed_library, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    _settings, store, review, entries = reviewed_library
    target = entries[0]
    saved = tmp_path / "saved-entry"
    original_path = _save_entry_directory(store, target, saved)
    store.delete_entry(target["id"])
    shutil.copytree(saved, original_path)
    transaction_id = next(iter(store.pending_deletions()))
    directory = store.runtime_dir / f"library-delete-{transaction_id}.tmp"
    journal = directory / "journal.json"
    original_fsync = store._scoped_deletions._fsync
    card_id = review.card_id(target["id"], "statement")
    payload = {"attempt": "A new test response", "confidence": 2, "overt": True}
    surviving_attempt = next(
        attempt for attempt in review._read()["pending_attempts"].values()
        if attempt["entry_id"] == entries[2]["id"]
    )

    def fail_ack_directory_fsync(path):
        if path == directory and json.loads(journal.read_text())["state"] == "review-complete":
            raise OSError("injected acknowledgment directory fsync failure")
        return original_fsync(path)

    with monkeypatch.context() as patch:
        patch.setattr(store._scoped_deletions, "_fsync", fail_ack_directory_fsync)
        with pytest.raises(StoreError, match="directory fsync"):
            review.reveal(card_id, payload)
        assert json.loads(journal.read_text())["state"] == "review-complete"
        compacted_log = review.log_path.read_bytes()
        # A visible rename does not prove durability. Ignoring this intent now
        # could let a later crash replay the old tombstone over a new grade.
        with pytest.raises(StoreError, match="directory fsync"):
            store.pending_deletions()
        with pytest.raises(StoreError, match="directory fsync"):
            review.reveal(card_id, payload)
        with pytest.raises(StoreError, match="directory fsync"):
            review.grade(surviving_attempt["card_id"], surviving_attempt["id"], 2)
        assert review.log_path.read_bytes() == compacted_log
        assert all(attempt["entry_id"] != target["id"]
                   for attempt in review._read()["pending_attempts"].values())

    attempt = review.reveal(card_id, payload)
    schedule = review.grade(card_id, attempt["attempt_id"], 2)
    assert schedule["repetitions"] == 1
    assert not store.pending_deletions()
    review.prune_to_current_library()
    assert sum(record["entry_id"] == target["id"] for record in _log_records(review)) == 1


def test_multiple_pending_deletions_purge_only_their_review_history(reviewed_library):
    settings, store, review, entries = reviewed_library
    before_state = review._read()
    deleted_ids = {entry["id"] for entry in entries[:2]}
    for entry in entries[:2]:
        store.delete_entry(entry["id"])
    assert len(store.pending_deletions()) == 2
    assert _pending_entry_ids(store) == deleted_ids
    restarted = create_app(settings, local_mode=True)
    _assert_cleanup(restarted.state.review, before_state, deleted_ids, {entries[2]["id"]})


def test_invalid_review_history_cannot_acknowledge_a_committed_deletion(reviewed_library):
    _settings, store, review, entries = reviewed_library
    before_state = review._read()
    state_bytes = review.state_path.read_bytes()
    log_bytes = review.log_path.read_bytes()
    deleted_id = entries[0]["id"]
    store.delete_entry(deleted_id)
    corrupted = log_bytes + b"not a valid review record\n"
    review.log_path.write_bytes(corrupted)
    with pytest.raises(StoreError, match="unreadable or invalid"):
        review.prune_to_current_library()
    assert _pending_entry_ids(store) == {deleted_id}
    assert review.state_path.read_bytes() == state_bytes
    assert review.log_path.read_bytes() == corrupted
    review.log_path.write_bytes(log_bytes)
    review.prune_to_current_library()
    _assert_cleanup(review, before_state, {deleted_id},
                    {entry["id"] for entry in entries[1:]})


def test_prepared_deletion_rolls_back_before_startup_can_compact_history(reviewed_library):
    settings, store, review, entries = reviewed_library
    state_bytes = review.state_path.read_bytes()
    log_bytes = review.log_path.read_bytes()
    store.delete_entry(entries[0]["id"])
    transaction_id = next(iter(store.pending_deletions()))
    journal = store.runtime_dir / f"library-delete-{transaction_id}.tmp" / "journal.json"
    value = json.loads(journal.read_text())
    # The moved roots and manifest are the same immediately before commit; only
    # its durable state still says prepared when a process stops at that point.
    value["state"] = "prepared"
    journal.write_text(json.dumps(value), encoding="utf-8")
    restarted = create_app(settings, local_mode=True)
    assert restarted.state.store.get_entry(entries[0]["id"])["title"] == entries[0]["title"]
    assert not restarted.state.store.pending_deletions()
    assert restarted.state.review.state_path.read_bytes() == state_bytes
    assert restarted.state.review.log_path.read_bytes() == log_bytes
