from __future__ import annotations

import json
from pathlib import Path

import pytest

from study_app.store import LibraryStore, StoreError


@pytest.fixture
def deletion_library(tmp_path: Path):
    store = LibraryStore(tmp_path / "data")
    folder = store.create_folder("Algebra", "algebra", None)
    deleted = store.create_entry(folder["id"], "df", "Group", "group", "", "Group body")
    survivor = store.create_entry(folder["id"], "df", "Ring", "ring", "", "Ring body")
    store.snapshot()
    return store, deleted, survivor


def _authored_bytes(store: LibraryStore) -> dict[str, bytes]:
    return {
        path.relative_to(store.library_dir).as_posix(): path.read_bytes()
        for path in store.library_dir.rglob("*") if path.is_file()
    }


def test_assetless_delete_skips_survivor_bodies_and_keeps_a_verified_cache(
    deletion_library, monkeypatch
):
    store, deleted, survivor = deletion_library

    def reject_asset_scan(*args):
        pytest.fail("a deletion with no candidate assets must not scan survivor Markdown")

    monkeypatch.setattr(store, "_surviving_asset_references", reject_asset_scan)
    result = store.delete_entry(deleted["id"])
    assert result["entry_count"] == 1
    assert store._library_cache is not None

    def reject_reparse():
        pytest.fail("unchanged data must reuse the fully validated post-delete snapshot")

    monkeypatch.setattr(store, "_read_uncached", reject_reparse)
    assert [entry["id"] for entry in store.snapshot()["entries"]] == [survivor["id"]]
    assert store.get_entry(survivor["id"])["formulations"][0]["content"] == "Ring body\n"


@pytest.mark.parametrize("change", ["metadata", "body", "invalid-metadata"])
def test_direct_edit_after_delete_validation_cannot_be_hidden_by_retained_cache(
    deletion_library, monkeypatch, change: str
):
    store, deleted, survivor = deletion_library
    source = store.data_dir / survivor["formulations"][0]["file"]
    original_write = store._scoped_deletions._write

    def commit_then_edit(directory, value, state):
        original_write(directory, value, state)
        if state != "committed":
            return
        if change == "body":
            source.write_text("External survivor body\n", encoding="utf-8")
        else:
            sidecar = source.parent / "_entry.json"
            metadata = json.loads(sidecar.read_text(encoding="utf-8"))
            metadata["title"] = "" if change == "invalid-metadata" else "External survivor title"
            sidecar.write_text(json.dumps(metadata), encoding="utf-8")

    monkeypatch.setattr(store._scoped_deletions, "_write", commit_then_edit)
    store.delete_entry(deleted["id"])
    if change == "invalid-metadata":
        with pytest.raises(StoreError):
            store.snapshot()
    else:
        current = store.get_entry(survivor["id"])
        if change == "body":
            assert current["formulations"][0]["content"] == "External survivor body\n"
        else:
            assert current["title"] == "External survivor title"


@pytest.mark.parametrize("failure", [StoreError, KeyboardInterrupt])
def test_delete_commit_failure_discards_new_cache_and_restores_original_tree(
    deletion_library, monkeypatch, failure: type[BaseException]
):
    store, deleted, _survivor = deletion_library
    before = _authored_bytes(store)
    store.search("Group body")

    original_write = store._scoped_deletions._write

    def fail_commit(directory, value, state):
        if state == "committed":
            raise failure("injected commit failure")
        return original_write(directory, value, state)

    monkeypatch.setattr(store._scoped_deletions, "_write", fail_commit)
    with pytest.raises(failure, match="injected commit failure"):
        store.delete_entry(deleted["id"])
    assert store._library_cache is None
    assert store._search_index is None
    assert _authored_bytes(store) == before
    assert store.get_entry(deleted["id"])["formulations"][0]["content"] == "Group body\n"
    assert LibraryStore(store.data_dir).check_data()["entries"] == 2
    assert store.pending_deletions() == {}


def test_delete_final_validation_failure_restores_original_tree(deletion_library, monkeypatch):
    store, deleted, _survivor = deletion_library
    before = _authored_bytes(store)

    def fail_validation(*args):
        raise StoreError("injected final validation failure")

    with monkeypatch.context() as patch:
        patch.setattr(store, "_verify_scoped_deletion", fail_validation)
        with pytest.raises(StoreError, match="injected final validation failure"):
            store.delete_entry(deleted["id"])
    assert store._library_cache is None
    assert _authored_bytes(store) == before
    assert store.get_entry(deleted["id"])["title"] == "Group"


def test_committed_delete_cleanup_failure_keeps_verified_current_tree(deletion_library, monkeypatch):
    store, deleted, survivor = deletion_library
    result = store.delete_entry(deleted["id"])
    pending = store.pending_deletions()
    store.complete_pending_deletions(pending)

    def fail_cleanup(*args, **kwargs):
        raise OSError("injected cleanup failure")

    with monkeypatch.context() as patch:
        patch.setattr("study_app.scoped_deletion.shutil.rmtree", fail_cleanup)
        store.cleanup_completed_deletions()
    assert result["entry_count"] == 1
    assert store._library_cache_is_current()
    assert list(store.runtime_dir.glob("library-delete-garbage-*.tmp"))
    reopened = LibraryStore(store.data_dir)
    assert [entry["id"] for entry in reopened.snapshot()["entries"]] == [survivor["id"]]
    assert reopened.pending_deletions() == {}
    reopened.cleanup_completed_deletions()
    assert not list(store.runtime_dir.glob("library-delete-garbage-*.tmp"))


def test_partial_trash_cleanup_cannot_block_reads_or_repeat_tombstones(deletion_library, monkeypatch):
    store, deleted, survivor = deletion_library
    store.delete_entry(deleted["id"])
    store.complete_pending_deletions(store.pending_deletions())

    def partial_cleanup(path, *args, **kwargs):
        (path / "journal.json").unlink(missing_ok=True)
        raise OSError("interrupted recursive unlink")

    with monkeypatch.context() as patch:
        patch.setattr("study_app.scoped_deletion.shutil.rmtree", partial_cleanup)
        store.cleanup_completed_deletions()
    assert store.get_entry(survivor["id"])["title"] == "Ring"
    reopened = LibraryStore(store.data_dir)
    assert reopened.pending_deletions() == {}
    assert reopened.check_data()["entries"] == 1
    reopened.cleanup_completed_deletions()
    assert not list(store.runtime_dir.glob("library-delete-garbage-*.tmp"))


def test_unpublished_preparation_is_inert_after_restart(deletion_library, monkeypatch):
    store, deleted, _survivor = deletion_library
    original_move = store._scoped_deletions._move

    def fail_publication(source, destination, **kwargs):
        if source.name.startswith("library-delete-preparing-"):
            raise KeyboardInterrupt("stop before publishing prepared journal")
        return original_move(source, destination, **kwargs)

    with monkeypatch.context() as patch:
        patch.setattr(store._scoped_deletions, "_move", fail_publication)
        # Simulate a hard process stop retaining the unpublished directory.
        patch.setattr("study_app.scoped_deletion.shutil.rmtree", lambda *args, **kwargs: None)
        with pytest.raises(KeyboardInterrupt):
            store.delete_entry(deleted["id"])
    assert list(store.runtime_dir.glob("library-delete-preparing-*.tmp"))
    reopened = LibraryStore(store.data_dir)
    assert reopened.pending_deletions() == {}
    assert reopened.get_entry(deleted["id"])["title"] == "Group"


def test_concurrent_survivor_edit_aborts_deletion_and_preserves_edit(deletion_library, monkeypatch):
    store, deleted, survivor = deletion_library
    path = store.data_dir / survivor["formulations"][0]["file"]
    original_verify = store._verify_scoped_deletion

    def edit_then_verify(before, mapping):
        path.write_text("Concurrent survivor edit\n", encoding="utf-8")
        return original_verify(before, mapping)

    monkeypatch.setattr(store, "_verify_scoped_deletion", edit_then_verify)
    with pytest.raises(StoreError, match="changed during deletion"):
        store.delete_entry(deleted["id"])
    assert store.get_entry(deleted["id"])["title"] == "Group"
    assert path.read_text() == "Concurrent survivor edit\n"
    assert store.pending_deletions() == {}


def test_edit_inside_detached_root_is_restored_on_abort(deletion_library, monkeypatch):
    store, deleted, _survivor = deletion_library
    source = store.data_dir / deleted["formulations"][0]["file"]
    original_verify = store._verify_scoped_deletion

    def edit_then_verify(before, mapping):
        saved_root = mapping[source.parent]
        (saved_root / source.name).write_text("Concurrent detached edit\n", encoding="utf-8")
        return original_verify(before, mapping)

    monkeypatch.setattr(store, "_verify_scoped_deletion", edit_then_verify)
    with pytest.raises(StoreError, match="changed during deletion"):
        store.delete_entry(deleted["id"])
    assert source.read_text() == "Concurrent detached edit\n"
    assert store.pending_deletions() == {}


def test_rollback_preserves_conflicting_new_live_directory(deletion_library, monkeypatch):
    import shutil

    store, deleted, _survivor = deletion_library
    source = store.data_dir / deleted["formulations"][0]["file"]

    def conflict_then_fail(before, mapping):
        shutil.copytree(mapping[source.parent], source.parent)
        source.write_text("New direct edit\n", encoding="utf-8")
        raise StoreError("injected conflict")

    monkeypatch.setattr(store, "_verify_scoped_deletion", conflict_then_fail)
    with pytest.raises(StoreError, match="injected conflict"):
        store.delete_entry(deleted["id"])
    assert source.read_text() == "Group body\n"
    conflicts = list(store.runtime_dir.glob(f"library-delete-*/conflicts/*/{source.name}"))
    assert len(conflicts) == 1
    assert conflicts[0].read_text() == "New direct edit\n"
    reopened = LibraryStore(store.data_dir)
    assert reopened.pending_deletions() == {}
    assert reopened.check_data()["entries"] == 2


def test_pending_journal_cannot_purge_an_unrelated_entry(deletion_library):
    store, deleted, survivor = deletion_library
    store.delete_entry(deleted["id"])
    journal = next(store.runtime_dir.glob("library-delete-*/journal.json"))
    value = json.loads(journal.read_text())
    value["entry_ids"] = [survivor["id"]]
    journal.write_text(json.dumps(value))
    with pytest.raises(StoreError, match="tombstones do not match"):
        store.pending_deletions()
    assert store.get_entry(survivor["id"])["title"] == "Ring"


def test_visible_ack_requires_durable_sync_for_retry_and_cleanup(deletion_library, monkeypatch):
    store, deleted, _survivor = deletion_library
    store.delete_entry(deleted["id"])
    pending = store.pending_deletions()
    original_sync = store._scoped_deletions._fsync

    def fail_ack_sync(path):
        if path.name.startswith("library-delete-"):
            raise OSError("injected acknowledgement sync failure")
        original_sync(path)

    with monkeypatch.context() as patch:
        patch.setattr(store._scoped_deletions, "_fsync", fail_ack_sync)
        for operation in (
            lambda: store.complete_pending_deletions(pending),
            lambda: store.complete_pending_deletions(pending),
            store.pending_deletions,
            store.cleanup_completed_deletions,
        ):
            with pytest.raises(StoreError, match="acknowledgement sync failure"):
                operation()
    assert list(store.runtime_dir.glob("library-delete-*/journal.json"))
    store.complete_pending_deletions(pending)
    store.cleanup_completed_deletions()
    assert store.pending_deletions() == {}
