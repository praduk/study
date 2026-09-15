from __future__ import annotations

from pathlib import Path

import pytest

from study_app.store import (
    V2_ENTRY_WRITE_JOURNAL,
    LibraryStore,
    StoreError,
    _atomic_json,
)


@pytest.mark.parametrize("interrupted_write", ["full-library", "entry"])
def test_warm_store_rejects_deletion_until_older_write_recovers(
    tmp_path: Path, interrupted_write: str,
):
    store = LibraryStore(tmp_path / "data")
    folder = store.create_folder("Fixture", "fixture", None)
    entry = store.create_entry(
        folder["id"], "df", "Fixture", "fixture", "", "Preserve these bytes.",
        review_enabled=False,
    )
    store.snapshot()
    body = store.data_dir / entry["formulations"][0]["file"]
    original = body.read_bytes()

    # Model another process dying after preparing an older write while this
    # store remains open. Deletion must not commit beside a rollback intent
    # that could resurrect the deleted entry on the next application startup.
    with store.mutation_lock:
        if interrupted_write == "full-library":
            store._begin_v2_transaction()
        else:
            metadata = body.parent / "_entry.json"
            _atomic_json(store.runtime_dir / V2_ENTRY_WRITE_JOURNAL, {
                "version": 1,
                "state": "prepared",
                "files": {
                    metadata.relative_to(store.data_dir).as_posix(): metadata.read_text(),
                },
            })

    with pytest.raises(StoreError, match="requires recovery"):
        store.delete_entry(entry["id"])
    assert body.read_bytes() == original
    assert store.pending_deletions() == {}

    reopened = LibraryStore(store.data_dir)
    assert {item["id"] for item in reopened.snapshot()["entries"]} == {entry["id"]}
    assert body.read_bytes() == original
    assert reopened.pending_deletions() == {}

    # Recovery restores availability as well as preserving the interrupted
    # write: a subsequent confirmed deletion can now complete normally.
    assert reopened.delete_entry(entry["id"])["entry_count"] == 1
    assert reopened.snapshot()["entries"] == []
