from __future__ import annotations

import json

import pytest
from fastapi.testclient import TestClient

import study_app.app as app_module
import study_app.store as store_module
from study_app.app import create_app
from study_app.store import LibraryStore, StoreError


def fixture(tmp_path):
    store = LibraryStore(tmp_path / "data", recovery_backups=False)
    source = store.create_folder("Source", "source", None)
    destination = store.create_folder("Destination", "destination", None)
    first = store.create_entry(source["id"], "df", "First", "first", "", "First body")
    second = store.create_entry(source["id"], "df", "Second", "second", "", "Second body")
    neighbor = store.create_entry(destination["id"], "df", "Neighbor", "neighbor", "", "Neighbor body")
    store.snapshot()
    return store, source, destination, first, second, neighbor


def test_move_avoids_library_copy_parse_and_unrelated_writes(tmp_path, monkeypatch):
    store, source, destination, first, second, neighbor = fixture(tmp_path)
    before = {path: path.read_bytes() for path in store.library_dir.rglob("*") if path.is_file()}
    original_path = (store.data_dir / first["formulations"][0]["file"]).parent
    original_inode = original_path.stat().st_ino

    def forbidden(*args, **kwargs):
        pytest.fail("an ordinary entry move must not copy or reparse the library")

    with monkeypatch.context() as scoped:
        scoped.setattr(store, "_begin_v2_transaction", forbidden)
        scoped.setattr(store, "_read_v2", forbidden)
        scoped.setattr(store_module.shutil, "copytree", forbidden)
        store.move_item("entry", first["id"], destination["id"], 0)
        moved = store.get_entry(first["id"])
        assert moved["canonical_tag"] == "destination:df:first"
        assert moved["formulations"][0]["content"] == "First body\n"
        assert (store.data_dir / moved["formulations"][0]["file"]).parent.stat().st_ino == original_inode
        snapshot = store.snapshot()
        assert [entry["id"] for entry in snapshot["tree"][1]["entries"]] == [first["id"], neighbor["id"]]
        store.move_item("entry", first["id"], source["id"], 1)
        assert [entry["id"] for entry in store.snapshot()["tree"][0]["entries"]] == [second["id"], first["id"]]
        store.move_item("entry", first["id"], source["id"], 0)
        assert [entry["id"] for entry in store.snapshot()["tree"][0]["entries"]] == [first["id"], second["id"]]
    for path, content in before.items():
        if path != original_path / "_entry.json":
            assert path.read_bytes() == content
    assert LibraryStore(store.data_dir).check_data()["entries"] == 3


def test_move_to_empty_folder_uses_fast_path(tmp_path, monkeypatch):
    store, source, _, first, _, _ = fixture(tmp_path)
    empty = store.create_folder("Empty", "empty", source["id"])
    store.snapshot()
    monkeypatch.setattr(store, "_read_v2", lambda *args: pytest.fail("unexpected complete parse"))
    store.move_item("entry", first["id"], empty["id"], 0)
    assert store.get_entry(first["id"])["canonical_tag"] == "source:empty:df:first"


def test_move_write_error_restores_location_and_metadata(tmp_path, monkeypatch):
    store, source, destination, first, _, _ = fixture(tmp_path)
    before = {path.relative_to(store.library_dir): path.read_bytes()
              for path in store.library_dir.rglob("*") if path.is_file()}
    original = store_module._atomic_json

    def fail_metadata(path, value):
        if path.name == "_entry.json" and "destination" in path.parts:
            raise OSError("simulated disk write failure")
        return original(path, value)

    monkeypatch.setattr(store_module, "_atomic_json", fail_metadata)
    with pytest.raises(StoreError, match="simulated disk write failure"):
        store.move_item("entry", first["id"], destination["id"], 0)
    assert store.get_entry(first["id"])["folder_id"] == source["id"]
    assert before == {path.relative_to(store.library_dir): path.read_bytes()
                      for path in store.library_dir.rglob("*") if path.is_file()}


def test_move_detects_concurrent_neighbor_change(tmp_path, monkeypatch):
    store, _, destination, first, second, _ = fixture(tmp_path)
    sidecar = (store.data_dir / second["formulations"][0]["file"]).parent / "_entry.json"
    original = store_module._atomic_json

    def change_neighbor(path, value):
        original(path, value)
        if path.name == "_entry.json" and path.parent.name == "first":
            data = json.loads(sidecar.read_text())
            data["title"] = "Changed outside Study"
            original(sidecar, data)

    monkeypatch.setattr(store_module, "_atomic_json", change_neighbor)
    store.move_item("entry", first["id"], destination["id"], 0)
    assert store.get_entry(second["id"])["title"] == "Changed outside Study"
    assert store.get_entry(first["id"])["folder_id"] == destination["id"]


def test_move_rank_exhaustion_falls_back_and_preserves_order(tmp_path):
    store, _, destination, first, _, neighbor = fixture(tmp_path)
    sidecar = (store.data_dir / neighbor["formulations"][0]["file"]).parent / "_entry.json"
    value = json.loads(sidecar.read_text())
    value["rank"] = 0
    sidecar.write_text(json.dumps(value))
    store.move_item("entry", first["id"], destination["id"], 0)
    reopened = LibraryStore(store.data_dir)
    assert [entry["id"] for entry in reopened.snapshot()["tree"][1]["entries"]] == [first["id"], neighbor["id"]]


def test_move_collision_leaves_both_entries_unchanged(tmp_path):
    store, source, destination, first, _, _ = fixture(tmp_path)
    conflict = store.create_entry(destination["id"], "df", "Conflict", "first", "", "Other body")
    with pytest.raises(StoreError, match="tag"):
        store.move_item("entry", first["id"], destination["id"], 0)
    assert store.get_entry(first["id"])["folder_id"] == source["id"]
    assert store.get_entry(conflict["id"])["formulations"][0]["content"] == "Other body\n"


def test_small_move_response_skips_snapshot_and_preserves_legacy_response(settings_factory, monkeypatch):
    monkeypatch.setattr(app_module, "_pdf_export_available", lambda: False)
    app = create_app(settings_factory(), local_mode=True)
    store = app.state.store
    source = store.create_folder("Source", "source", None)
    destination = store.create_folder("Destination", "destination", None)
    entry = store.create_entry(source["id"], "df", "First", "first", "", "Body")
    with TestClient(app, base_url="http://127.0.0.1", client=("127.0.0.1", 50000)) as client:
        url = f"/api/items/entry/{entry['id']}/move"
        headers = {"origin": "http://127.0.0.1", "x-study-csrf": "local"}
        with monkeypatch.context() as scoped:
            scoped.setattr(store, "snapshot", lambda **kwargs: pytest.fail("unused snapshot"))
            response = client.post(url + "?include_library=false", headers=headers,
                                   json={"destination_folder_id": destination["id"], "index": 0})
            assert response.status_code == 200, response.text
            assert response.content == b'{"ok":true}'
        response = client.post(url, headers=headers,
                               json={"destination_folder_id": source["id"], "index": 0})
        assert response.status_code == 200
        assert response.json()["library"]["entries"][0]["folder_id"] == source["id"]
