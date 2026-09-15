from __future__ import annotations

import json
from pathlib import Path

import pytest

from study_app.store import LibraryStore, StoreError


def _library(tmp_path: Path):
    store = LibraryStore(tmp_path / "data")
    folder = store.create_folder("Algebra", "algebra", None)
    first = store.create_entry(folder["id"], "df", "Group", "group", "", "Group body")
    second = store.create_entry(folder["id"], "th", "Order", "order", "", "Order body")
    store.add_supplement(
        second["id"], {"kind": "pf", "label": "Proof", "content": "Proof body", "main": True}
    )
    store.snapshot()
    return store, first, second


def test_flat_snapshot_does_not_build_tree(tmp_path: Path, monkeypatch):
    store, _first, _second = _library(tmp_path)
    full = store.snapshot()

    def unexpected_tree(*args):
        pytest.fail("flat snapshots must not build the discarded tree")

    monkeypatch.setattr(store, "_tree", unexpected_tree)
    assert store.snapshot(include_tree=False) == {
        key: value for key, value in full.items() if key != "tree"
    }


def test_read_results_cannot_mutate_cached_library(tmp_path: Path):
    store, first, second = _library(tmp_path)
    original = store.snapshot()
    snapshot = store.snapshot()
    snapshot["folders"][0]["name"] = "Changed folder"
    snapshot["entries"][0]["formulations"][0]["label"] = "Changed label"
    snapshot["tree"][0]["entries"][0]["review_modes"].append("invalid")
    hydrated = store.get_entries([first["id"], second["id"]])
    hydrated[first["id"]]["title"] = "Changed entry"
    hydrated[second["id"]]["supplements"][0]["content"] = "Changed proof"

    assert store.snapshot() == original
    assert store.get_entry(first["id"])["title"] == first["title"]
    assert store.get_entry(second["id"])["supplements"][0]["content"] == "Proof body\n"


def test_entry_batch_validates_once_and_reads_only_selected_content(tmp_path: Path, monkeypatch):
    store, first, second = _library(tmp_path)
    expected = store.get_entry(second["id"])
    checks = 0
    read_paths = []
    original_current = store._library_cache_is_current
    original_content = store._read_content

    def count_check():
        nonlocal checks
        checks += 1
        return original_current()

    def count_content(relative):
        read_paths.append(relative)
        return original_content(relative)

    monkeypatch.setattr(store, "_library_cache_is_current", count_check)
    monkeypatch.setattr(store, "_read_content", count_content)
    assert store.get_entries(iter([second["id"], second["id"]])) == {second["id"]: expected}
    assert checks == 1
    assert read_paths == [
        variant["file"] for variant in expected["formulations"] + expected["supplements"]
    ]
    assert first["formulations"][0]["file"] not in read_paths
    assert store.get_entries([]) == {}
    assert checks == 1
    with pytest.raises(StoreError, match="entry not found"):
        store.get_entries(["missing"])


@pytest.mark.parametrize("reader", ["snapshot", "entry", "batch"])
def test_read_view_immediately_rejects_invalid_direct_metadata_edit(tmp_path: Path, reader: str):
    store, first, _second = _library(tmp_path)
    sidecar = next(store.library_dir.rglob("group/_entry.json"))
    metadata = json.loads(sidecar.read_text(encoding="utf-8"))
    metadata["review_enabled"] = "invalid"
    sidecar.write_text(json.dumps(metadata), encoding="utf-8")

    with pytest.raises(StoreError, match="review_enabled"):
        if reader == "snapshot":
            store.snapshot(include_tree=False)
        elif reader == "entry":
            store.get_entry(first["id"])
        else:
            store.get_entries([first["id"]])


def test_warm_entry_reads_immediately_refresh_direct_edits(tmp_path: Path):
    store, first, _second = _library(tmp_path)
    entry = store.get_entry(first["id"])
    source = store.data_dir / entry["formulations"][0]["file"]
    source.write_text("Directly edited body\n", encoding="utf-8")
    sidecar = source.parent / "_entry.json"
    metadata = json.loads(sidecar.read_text(encoding="utf-8"))
    metadata["title"] = "Directly edited title"
    sidecar.write_text(json.dumps(metadata), encoding="utf-8")

    changed = store.get_entry(first["id"])
    assert changed["title"] == "Directly edited title"
    assert changed["formulations"][0]["content"] == "Directly edited body\n"


def test_tree_signature_scan_covers_every_file_and_directory(tmp_path: Path):
    store, _first, _second = _library(tmp_path)
    expected_paths = {store.library_dir, *store.library_dir.rglob("*")}
    assert store._v2_tree_signatures() == {
        path: store._file_signature(path) for path in expected_paths
    }


def test_tree_signature_scan_records_but_does_not_follow_symlinks(tmp_path: Path):
    store, _first, _second = _library(tmp_path)
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "outside.md").write_text("Outside", encoding="utf-8")
    link = store.library_dir / "linked"
    try:
        link.symlink_to(outside, target_is_directory=True)
    except OSError:
        pytest.skip("symbolic links are unavailable")
    signatures = store._v2_tree_signatures()
    assert signatures[link] == store._file_signature(link)
    assert link / "outside.md" not in signatures
    with pytest.raises(StoreError, match="symbolic links"):
        store.snapshot()


def test_indexed_content_rechecks_ancestor_after_signature_read(tmp_path: Path, monkeypatch):
    store, first, _second = _library(tmp_path)
    relative = first["formulations"][0]["file"]
    source = store.data_dir / relative
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / source.name).write_text("Outside content", encoding="utf-8")
    probe = tmp_path / "link-probe"
    try:
        probe.symlink_to(outside, target_is_directory=True)
    except OSError:
        pytest.skip("symbolic links are unavailable")
    probe.unlink()
    original_signature = store._file_signature
    replaced = False

    def signature_then_replace_ancestor(path):
        nonlocal replaced
        signature = original_signature(path)
        if path == source and not replaced:
            replaced = True
            source.parent.rename(tmp_path / "displaced-entry")
            source.parent.symlink_to(outside, target_is_directory=True)
        return signature

    monkeypatch.setattr(store, "_file_signature", signature_then_replace_ancestor)
    with pytest.raises(StoreError, match="inside the active library root"):
        store._read_indexed_content(relative)
