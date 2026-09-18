from __future__ import annotations

import hashlib
import io
import json
from types import SimpleNamespace

import pytest
from PIL import Image

import study_app.store as store_module
from study_app.store import LibraryStore, StoreError


def test_creation_and_folder_changes_skip_full_parse_and_preserve_subtree(tmp_path, monkeypatch):
    store = LibraryStore(tmp_path / "data", recovery_backups=False)
    root = store.create_folder("Root", "root", None)
    nested = store.create_folder("Nested", "nested", root["id"])
    entry = store.create_entry(nested["id"], "df", "First", "first", "", "Body with @first")
    source = store._v2_folder_paths[root["id"]]
    files = {path.relative_to(source): (path.read_bytes(), path.stat().st_ino)
             for path in source.rglob("*") if path.is_file()}
    store.resolve_reference(nested["id"], "first")

    def forbidden(*args, **kwargs):
        pytest.fail("routine structural writes must not reparse or copy the library")

    with monkeypatch.context() as scoped:
        scoped.setattr(store, "_read_v2", forbidden)
        scoped.setattr(store_module.shutil, "copytree", forbidden)
        other = store.create_folder("Other", "other", None, index=0)
        second = store.create_entry(nested["id"], "df", "Second", "second", "", "Second", index=0)
        store.update_folder(root["id"], {"name": "Renamed", "slug": "renamed"})
        store.move_item("folder", root["id"], other["id"], 0)
        moved = store.get_entry(entry["id"])
        assert moved["canonical_tag"] == "other:renamed:nested:df:first"
        assert moved["formulations"][0]["content"] == "Body with @first\n"
        assert store.resolve_reference(nested["id"], "other:renamed:nested:df:first")["status"] == "resolved"
        store.move_item("folder", root["id"], None, 0)
        store.move_item("folder", other["id"], None, 0)
    destination = store._v2_folder_paths[root["id"]]
    for relative, (body, inode) in files.items():
        if relative.as_posix() == "_folder.json":
            continue
        assert (destination / relative).read_bytes() == body
        assert (destination / relative).stat().st_ino == inode
    reopened = LibraryStore(store.data_dir)
    assert reopened.check_data()["entries"] == 2
    assert [item["id"] for item in reopened.snapshot()["tree"][1]["children"][0]["entries"]] == [second["id"], entry["id"]]


@pytest.mark.parametrize("operation", ["folder", "entry", "rename", "move"])
def test_structural_write_detects_unexpected_external_edit(tmp_path, monkeypatch, operation):
    store = LibraryStore(tmp_path / "data", recovery_backups=False)
    root = store.create_folder("Root", "root", None)
    other = store.create_folder("Other", "other", None)
    entry = store.create_entry(other["id"], "df", "First", "first", "", "Body")
    sidecar = store._v2_entry_paths[entry["id"]] / "_entry.json"
    original = store_module._atomic_text

    def write_and_edit(path, text):
        original(path, text)
        value = json.loads(sidecar.read_text())
        value["title"] = "External edit"
        sidecar.write_text(json.dumps(value))

    monkeypatch.setattr(store_module, "_atomic_text", write_and_edit)
    if operation == "folder":
        store.create_folder("Added", "added", None)
    elif operation == "entry":
        store.create_entry(root["id"], "df", "Added", "added", "", "Added")
    elif operation == "rename":
        store.update_folder(root["id"], {"slug": "renamed"})
    else:
        store.move_item("folder", root["id"], other["id"], 0)
    assert store.get_entry(entry["id"])["title"] == "External edit"
    assert LibraryStore(store.data_dir).get_entry(entry["id"])["title"] == "External edit"


def test_new_records_cannot_reuse_variant_ids(tmp_path, monkeypatch):
    store = LibraryStore(tmp_path / "data", recovery_backups=False)
    root = store.create_folder("Root", "root", None)
    entry = store.create_entry(root["id"], "df", "First", "first", "", "Body")
    before = {path: path.read_bytes() for path in store.library_dir.rglob("*") if path.is_file()}
    monkeypatch.setattr(store_module.uuid, "uuid4", lambda: SimpleNamespace(hex=entry["formulations"][0]["id"]))
    with pytest.raises(StoreError, match="duplicate record id"):
        store.create_folder("Collision", "collision", None)
    assert before == {path: path.read_bytes() for path in store.library_dir.rglob("*") if path.is_file()}


def test_new_entry_with_exhausted_rank_gap_persists_authored_order(tmp_path):
    store = LibraryStore(tmp_path / "data", recovery_backups=False)
    root = store.create_folder("Root", "root", None)
    first = store.create_entry(root["id"], "df", "First", "first", "", "Body")
    metadata = store._v2_entry_paths[first["id"]] / "_entry.json"
    value = json.loads(metadata.read_text())
    value["rank"] = 0
    metadata.write_text(json.dumps(value))
    added = store.create_entry(root["id"], "df", "Added", "added", "", "Added", index=0)
    assert [entry["id"] for entry in LibraryStore(store.data_dir).snapshot()["tree"][0]["entries"]] == [added["id"], first["id"]]


def test_deep_folder_path_transition_uses_general_writer(tmp_path, monkeypatch):
    monkeypatch.setattr(store_module, "V2_MAX_RELATIVE_PATH", 400)
    store = LibraryStore(tmp_path / "data", recovery_backups=False)
    parent = None
    for i in range(5):
        folder = store.create_folder(f"Level {i}", "a" * 40 + str(i), parent)
        parent = folder["id"]
    entry = store.create_entry(parent, "df", "Deep", "deep", "", "Body")
    assert store._v2_folder_paths[parent].parent.name == "_deep"
    store.move_item("folder", parent, None, 0)
    assert LibraryStore(store.data_dir).get_entry(entry["id"])["canonical_tag"] == folder["slug"] + ":df:deep"


def test_folder_move_preserves_owned_asset_paths_without_rewriting_files(tmp_path, monkeypatch):
    store = LibraryStore(tmp_path / "data", recovery_backups=False)
    root = store.create_folder("Root", "root", None)
    other = store.create_folder("Other", "other", None)
    entry = store.create_entry(root["id"], "df", "Image", "image", "", "Body")
    stream = io.BytesIO()
    Image.new("RGB", (4, 3), "white").save(stream, format="PNG")
    image = stream.getvalue()
    filename = hashlib.sha256(image).hexdigest() + ".png"
    store.register_asset(entry["id"], {
        "id": "b" * 32, "kind": "image", "path": "media/" + filename,
        "alt": "Fixture", "width": 76, "invert_lightness": False, "pixels": [4, 3],
    }, {"path": image})
    old_asset = store.resolve_media_file(filename)
    inode = old_asset.stat().st_ino
    monkeypatch.setattr(store, "_read_v2", lambda *args: pytest.fail("unexpected full parse"))
    store.move_item("folder", root["id"], other["id"], 0)
    moved = store.get_entry(entry["id"])
    path = store.resolve_media_file(filename)
    assert path.read_bytes() == image
    assert path.stat().st_ino == inode
    assert not old_asset.exists()
    assert LibraryStore(store.data_dir).get_entry(entry["id"])["assets"] == moved["assets"]
