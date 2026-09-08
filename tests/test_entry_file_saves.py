from __future__ import annotations

import json
from pathlib import Path

import pytest

import study_app.store as store_module
from study_app.store import V2_ENTRY_WRITE_JOURNAL, LibraryStore, StoreError


@pytest.fixture
def entry_library(tmp_path: Path):
    store = LibraryStore(tmp_path / "data")
    folder = store.create_folder("Algebra", "algebra", None)
    entry = store.create_entry(folder["id"], "df", "Group", "group", "", "Original")
    other = store.create_entry(folder["id"], "df", "Ring", "ring", "", "Unrelated")
    return store, entry, other


def _paths(store: LibraryStore, entry: dict) -> tuple[Path, Path]:
    content = store.data_dir / entry["formulations"][0]["file"]
    return content, content.parent / "_entry.json"


def _authored_bytes(store: LibraryStore) -> dict[Path, bytes]:
    return {path: path.read_bytes() for path in store.library_dir.rglob("*") if path.is_file()}


def _journal(store: LibraryStore, entry: dict, *, state: str = "prepared") -> dict:
    return {
        "version": 1,
        "state": state,
        "files": {
            path.relative_to(store.data_dir).as_posix(): path.read_text(encoding="utf-8")
            for path in _paths(store, entry)
        },
    }


@pytest.mark.parametrize("operation", ["content", "metadata"])
def test_existing_entry_save_writes_only_its_changed_files(
    entry_library, monkeypatch: pytest.MonkeyPatch, operation: str
):
    store, entry, other = entry_library
    content, metadata = _paths(store, entry)
    store.get_entry(entry["id"])
    before = _authored_bytes(store)
    writes = []
    atomic_text = store_module._atomic_text

    def record_write(path: Path, text: str):
        writes.append(path)
        atomic_text(path, text)

    def reject_full_tree_work(*args, **kwargs):
        pytest.fail("an ordinary entry save must not copy or reparse the entire library")

    monkeypatch.setattr(store_module, "_atomic_text", record_write)
    monkeypatch.setattr(store_module.shutil, "copytree", reject_full_tree_work)
    monkeypatch.setattr(store, "_apply_v2_write", reject_full_tree_work)
    monkeypatch.setattr(store, "_read_v2", reject_full_tree_work)
    if operation == "content":
        result = store.write_variant_content(entry["id"], entry["formulations"][0]["id"], "Saved")
        expected = {content, metadata}
        assert result["formulations"][0]["content"] == "Saved\n"
    else:
        result = store.update_entry(entry["id"], {"title": "Saved title", "header": "Context"})
        expected = {metadata}
        assert result["title"] == "Saved title"
        assert result["header"] == "Context"

    after = _authored_bytes(store)
    assert set(before) == set(after)
    assert {path for path in before if before[path] != after[path]} == expected
    assert {path for path in writes if store.library_dir in path.parents} == expected
    assert store.get_entry(other["id"])["formulations"][0]["content"] == "Unrelated\n"
    assert not (store.runtime_dir / V2_ENTRY_WRITE_JOURNAL).exists()


def test_unchanged_entry_save_preserves_timestamp_and_search_snapshot(
    entry_library, monkeypatch: pytest.MonkeyPatch
):
    store, entry, _ = entry_library
    store.linked_items(entry["id"])
    index = store._search_index
    before = _authored_bytes(store)

    def reject_write(*args, **kwargs):
        pytest.fail("saving unchanged values must not rewrite authored files or a journal")

    monkeypatch.setattr(store_module, "_atomic_text", reject_write)
    metadata_result = store.update_entry(
        entry["id"], {"title": entry["title"], "kind": entry["kind"], "header": ""}
    )
    content_result = store.write_variant_content(
        entry["id"], entry["formulations"][0]["id"], "Original\n\n"
    )
    assert metadata_result["updated_at"] == entry["updated_at"]
    assert content_result["updated_at"] == entry["updated_at"]
    assert store._search_index is index
    assert _authored_bytes(store) == before


@pytest.mark.parametrize("failure", [OSError, KeyboardInterrupt])
def test_second_entry_file_write_failure_restores_bytes_and_reopens(
    entry_library, monkeypatch: pytest.MonkeyPatch, failure: type[BaseException]
):
    store, entry, _ = entry_library
    content, metadata = _paths(store, entry)
    before = _authored_bytes(store)
    atomic_text = store_module._atomic_text
    failed = False

    def fail_metadata_once(path: Path, text: str):
        nonlocal failed
        if path == metadata and not failed:
            failed = True
            assert content.read_text(encoding="utf-8") == "Interrupted\n"
            raise failure("injected second-file failure")
        atomic_text(path, text)

    monkeypatch.setattr(store_module, "_atomic_text", fail_metadata_once)
    with pytest.raises(failure, match="injected second-file failure"):
        store.write_variant_content(
            entry["id"], entry["formulations"][0]["id"], "Interrupted"
        )

    assert failed
    assert _authored_bytes(store) == before
    reopened = LibraryStore(store.data_dir)
    assert reopened.get_entry(entry["id"])["formulations"][0]["content"] == "Original\n"
    assert not (store.runtime_dir / V2_ENTRY_WRITE_JOURNAL).exists()
    preserved = list(store.runtime_dir.glob("library-entry-failed-*.tmp"))
    assert len(preserved) == 1
    assert (preserved[0] / content.name).read_text(encoding="utf-8") == "Interrupted\n"


def test_prepared_entry_journal_recovers_only_its_entry_and_preserves_displaced_edits(
    entry_library,
):
    store, entry, other = entry_library
    content, metadata = _paths(store, entry)
    other_content, other_metadata = _paths(store, other)
    journal_path = store.runtime_dir / V2_ENTRY_WRITE_JOURNAL
    journal_path.write_text(json.dumps(_journal(store, entry)), encoding="utf-8")
    content.write_text("Direct edit after interruption\n", encoding="utf-8")
    changed_metadata = json.loads(metadata.read_text(encoding="utf-8"))
    changed_metadata["title"] = "Displaced title"
    metadata.write_text(json.dumps(changed_metadata), encoding="utf-8")
    other_content.write_text("Unrelated direct edit\n", encoding="utf-8")
    other_before = other_metadata.read_bytes()

    reopened = LibraryStore(store.data_dir)

    recovered = reopened.get_entry(entry["id"])
    assert recovered["title"] == "Group"
    assert recovered["formulations"][0]["content"] == "Original\n"
    assert reopened.get_entry(other["id"])["formulations"][0]["content"] == "Unrelated direct edit\n"
    assert other_metadata.read_bytes() == other_before
    assert not journal_path.exists()
    preserved = list(store.runtime_dir.glob("library-entry-failed-*.tmp"))
    assert len(preserved) == 1
    assert {path.name for path in preserved[0].iterdir()} == {content.name, metadata.name}
    assert (preserved[0] / content.name).read_text(encoding="utf-8") == (
        "Direct edit after interruption\n"
    )
    assert json.loads((preserved[0] / metadata.name).read_text())["title"] == "Displaced title"


def test_committed_entry_save_survives_journal_cleanup_failure(
    entry_library, monkeypatch: pytest.MonkeyPatch
):
    store, entry, _ = entry_library
    journal_path = store.runtime_dir / V2_ENTRY_WRITE_JOURNAL
    unlink = Path.unlink

    def fail_cleanup(path: Path, *args, **kwargs):
        if path == journal_path:
            raise OSError("injected cleanup failure")
        return unlink(path, *args, **kwargs)

    with monkeypatch.context() as patch:
        patch.setattr(Path, "unlink", fail_cleanup)
        result = store.write_variant_content(
            entry["id"], entry["formulations"][0]["id"], "Committed"
        )
    assert result["formulations"][0]["content"] == "Committed\n"
    assert json.loads(journal_path.read_text())["state"] == "committed"
    reopened = LibraryStore(store.data_dir)
    assert reopened.get_entry(entry["id"])["formulations"][0]["content"] == "Committed\n"
    assert not journal_path.exists()
    assert not list(store.runtime_dir.glob("library-entry-failed-*.tmp"))


@pytest.mark.parametrize(
    "unsafe",
    ["absolute", "escape", "traversal", "other-entry", "unlisted", "invalid-metadata", "symlink"],
)
def test_unsafe_entry_journal_is_rejected_before_any_live_file_is_replaced(
    entry_library, tmp_path: Path, unsafe: str
):
    store, entry, other = entry_library
    content, metadata = _paths(store, entry)
    value = _journal(store, entry)
    outside = tmp_path / "outside.md"
    outside.write_text("Outside original\n", encoding="utf-8")
    if unsafe == "absolute":
        value["files"][str(outside)] = "Untrusted replacement"
    elif unsafe == "escape":
        value["files"]["../outside.md"] = "Untrusted replacement"
    elif unsafe == "traversal":
        relative = content.relative_to(store.data_dir)
        value["files"][f"{relative.parent}/../{relative.parent.name}/{relative.name}"] = "Bad"
    elif unsafe == "other-entry":
        other_content, _ = _paths(store, other)
        value["files"][other_content.relative_to(store.data_dir).as_posix()] = "Bad"
    elif unsafe == "unlisted":
        value["files"][metadata.with_name("unlisted.md").relative_to(store.data_dir).as_posix()] = "Bad"
    elif unsafe == "invalid-metadata":
        prior = json.loads(value["files"][metadata.relative_to(store.data_dir).as_posix()])
        prior["title"] = ""
        value["files"][metadata.relative_to(store.data_dir).as_posix()] = json.dumps(prior)
    elif unsafe == "symlink":
        content.unlink()
        content.symlink_to(outside)
    else:
        raise AssertionError(unsafe)
    before = _authored_bytes(store)
    journal_path = store.runtime_dir / V2_ENTRY_WRITE_JOURNAL
    journal_path.write_text(json.dumps(value), encoding="utf-8")

    with pytest.raises(StoreError):
        LibraryStore(store.data_dir)

    assert _authored_bytes(store) == before
    assert outside.read_text(encoding="utf-8") == "Outside original\n"
    assert journal_path.exists()
    assert not list(store.runtime_dir.glob("library-entry-failed-*.tmp"))


@pytest.mark.parametrize("changed", ["target-metadata", "other-metadata", "other-content", "new-file"])
def test_direct_edit_during_entry_save_cannot_be_attached_to_a_stale_cache(
    entry_library, monkeypatch: pytest.MonkeyPatch, changed: str
):
    store, entry, other = entry_library
    content, metadata = _paths(store, entry)
    other_content, other_metadata = _paths(store, other)
    refresh = store._refresh_v2_entry_cache
    invalidated = False

    def edit_before_cache_refresh(*args):
        nonlocal invalidated
        if changed in {"target-metadata", "other-metadata"}:
            path = metadata if changed == "target-metadata" else other_metadata
            value = json.loads(path.read_text(encoding="utf-8"))
            value["title"] = "External title"
            path.write_text(json.dumps(value), encoding="utf-8")
        elif changed == "other-content":
            other_content.write_text("External body\n", encoding="utf-8")
        else:
            content.with_name("unlisted.md").write_text("External file\n", encoding="utf-8")
        refresh(*args)
        invalidated = store._library_cache is None

    monkeypatch.setattr(store, "_refresh_v2_entry_cache", edit_before_cache_refresh)
    if changed == "new-file":
        with pytest.raises(StoreError, match="unrecognized path"):
            store.write_variant_content(entry["id"], entry["formulations"][0]["id"], "Saved")
        assert store._library_cache is None
    else:
        store.write_variant_content(entry["id"], entry["formulations"][0]["id"], "Saved")
        if changed == "other-content":
            assert store.get_entry(other["id"])["formulations"][0]["content"] == "External body\n"
        else:
            changed_entry = entry if changed == "target-metadata" else other
            assert store.get_entry(changed_entry["id"])["title"] == "External title"
    assert invalidated
    assert content.read_text(encoding="utf-8") == "Saved\n"


def test_valid_uppercase_markdown_variant_remains_editable(entry_library):
    store, entry, _ = entry_library
    content, metadata = _paths(store, entry)
    uppercase = content.with_suffix(".MD")
    content.rename(uppercase)
    value = json.loads(metadata.read_text(encoding="utf-8"))
    value["formulations"][0]["file"] = uppercase.name
    metadata.write_text(json.dumps(value), encoding="utf-8")
    reopened = LibraryStore(store.data_dir)
    assert reopened.check_data()["entries"] == 2

    reopened.write_variant_content(entry["id"], entry["formulations"][0]["id"], "Uppercase saved")

    assert uppercase.read_text(encoding="utf-8") == "Uppercase saved\n"
    assert LibraryStore(store.data_dir).get_entry(entry["id"])["formulations"][0]["content"] == (
        "Uppercase saved\n"
    )
