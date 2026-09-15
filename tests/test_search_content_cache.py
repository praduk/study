from __future__ import annotations

import os
from pathlib import Path

import pytest

import study_app.store as store_module
from study_app.search_index import SearchIndexError
from study_app.store import LibraryStore, StoreError


@pytest.fixture
def indexed_library(tmp_path: Path):
    store = LibraryStore(tmp_path / "data")
    folder = store.create_folder("Algebra", "algebra", None)
    first = store.create_entry(folder["id"], "df", "Group", "group", "", "Original")
    second = store.create_entry(folder["id"], "df", "Ring", "ring", "", "See @group.")
    store.search("Original")
    return store, first, second


def test_metadata_rebuild_reuses_bodies_but_refreshes_titles_and_links(indexed_library):
    store, first, second = indexed_library
    original_revision = store.linked_items(first["id"])["revision"]
    reads = store.search_index_stats()["content_reads"]

    store.update_entry(second["id"], {"title": "New source title"})

    assert store.search("New source title")[0]["id"] == second["id"]
    assert store.search_index_stats()["content_reads"] == reads
    linked = store.linked_items(first["id"])
    assert linked["revision"] != original_revision
    assert linked["items"][0]["title"] == "New source title"
    assert store.resolve_reference(second["folder_id"], "ring")["match"]["title"] == (
        "New source title"
    )


def test_one_body_edit_reads_only_that_file_and_rebuilds_backlinks(indexed_library):
    store, first, second = indexed_library
    assert store.linked_items(first["id"])["total"] == 1
    reads = store.search_index_stats()["content_reads"]

    store.write_variant_content(
        second["id"], second["formulations"][0]["id"], "Replacement body without references"
    )

    assert store.search("Replacement body")[0]["id"] == second["id"]
    assert store.search_index_stats()["content_reads"] == reads + 1
    assert store.linked_items(first["id"])["total"] == 0


@pytest.mark.parametrize("replacement", [False, True])
def test_same_size_and_mtime_external_changes_are_not_reused(indexed_library, replacement: bool):
    store, first, _second = indexed_library
    source = store.data_dir / first["formulations"][0]["file"]
    before = source.stat()
    reads = store.search_index_stats()["content_reads"]
    target = source.with_name("replacement.tmp") if replacement else source
    target.write_text("External\n", encoding="utf-8")
    os.utime(target, ns=(before.st_atime_ns, before.st_mtime_ns))
    if replacement:
        os.replace(target, source)
    assert source.stat().st_size == before.st_size
    assert source.stat().st_mtime_ns == before.st_mtime_ns

    store.reload_search_index()

    assert store.search("Original") == []
    assert store.search("External")[0]["id"] == first["id"]
    assert store.search_index_stats()["content_reads"] == reads + 1


def test_cached_body_edit_during_rebuild_retries_before_publication(indexed_library, monkeypatch):
    store, first, second = indexed_library
    source = store.data_dir / first["formulations"][0]["file"]
    reads = store.search_index_stats()["content_reads"]
    original_read_view = store._read_view
    edited = False

    def read_then_edit():
        nonlocal edited
        library = original_read_view()
        if not edited:
            edited = True
            source.write_text("Concurrent body\n", encoding="utf-8")
        return library

    store.update_entry(second["id"], {"title": "Changed title"})
    monkeypatch.setattr(store, "_read_view", read_then_edit)

    assert store.search("Concurrent body")[0]["id"] == first["id"]
    assert store.search("Original") == []
    assert store.search_index_stats()["content_reads"] == reads + 1


def test_failed_index_construction_does_not_publish_cached_bytes(indexed_library, monkeypatch):
    store, first, _second = indexed_library
    committed_cache = store._search_content_cache
    committed_index = store._search_index
    reads = store.search_index_stats()["content_reads"]
    store.write_variant_content(first["id"], first["formulations"][0]["id"], "Changed body")

    def fail_construction(*args, **kwargs):
        raise SearchIndexError("injected index construction failure")

    with monkeypatch.context() as patch:
        patch.setattr(store_module, "LibrarySearchIndex", fail_construction)
        with pytest.raises(StoreError, match="injected index construction failure"):
            store.search("Changed body")

    assert store._search_content_cache is committed_cache
    assert store._search_index is None
    assert store._last_search_index is committed_index
    assert store.search("Changed body")[0]["id"] == first["id"]
    assert store._last_search_index is store._search_index
    assert store._last_search_index is not committed_index
    assert store.search_index_stats()["content_reads"] == reads + 2


def test_repeated_concurrent_edits_do_not_publish_a_partial_content_cache(
    indexed_library, monkeypatch
):
    store, first, _second = indexed_library
    source = store.data_dir / first["formulations"][0]["file"]
    committed_cache = store._search_content_cache
    original_read_view = store._read_view
    edits = 0

    def read_then_edit():
        nonlocal edits
        library = original_read_view()
        edits += 1
        source.write_text(f"Concurrent body {edits}\n", encoding="utf-8")
        return library

    monkeypatch.setattr(store, "_read_view", read_then_edit)
    with pytest.raises(StoreError, match="changed repeatedly"):
        store.reload_search_index()
    assert store._search_content_cache is committed_cache
    assert store._search_index is None


def test_completed_content_cache_adds_and_prunes_current_library_paths(indexed_library):
    store, first, second = indexed_library
    third = store.create_entry(first["folder_id"], "df", "Field", "field", "", "Field body")
    assert store.search("Field body")[0]["id"] == third["id"]
    assert len(store._search_content_cache) == 3

    store.delete_entry(first["id"])
    store.search("Field body")

    assert set(store._search_content_cache) == {
        entry["formulations"][0]["file"] for entry in (second, third)
    }


@pytest.mark.parametrize("corruption", ["file-symlink", "ancestor-symlink", "missing"])
def test_cached_content_does_not_mask_unsafe_or_missing_paths(
    indexed_library, tmp_path: Path, corruption: str
):
    store, first, _second = indexed_library
    source = store.data_dir / first["formulations"][0]["file"]
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / source.name).write_text("External\n", encoding="utf-8")
    if corruption == "missing":
        source.unlink()
    else:
        probe = tmp_path / "link-probe"
        try:
            probe.symlink_to(outside, target_is_directory=True)
        except OSError:
            pytest.skip("symbolic links are unavailable")
        probe.unlink()
        if corruption == "file-symlink":
            source.unlink()
            source.symlink_to(outside / source.name)
        else:
            source.parent.rename(tmp_path / "displaced")
            source.parent.symlink_to(outside, target_is_directory=True)

    with pytest.raises(StoreError):
        store.reload_search_index()
    assert store._search_index is None


def test_v1_rebuilds_continue_to_read_every_markdown_file(tmp_path: Path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "library.json").write_text(
        '{"version": 1, "folders": [], "entries": []}\n', encoding="utf-8"
    )
    store = LibraryStore(data_dir)
    folder = store.create_folder("Algebra", "algebra", None)
    entry = store.create_entry(folder["id"], "df", "Group", "group", "", "Body")
    store.search("Body")
    reads = store.search_index_stats()["content_reads"]
    store.update_entry(entry["id"], {"title": "Changed title"})
    assert store.search("Changed title")[0]["id"] == entry["id"]
    assert store.search_index_stats()["content_reads"] == reads + 1
    assert store._search_content_cache == {}
