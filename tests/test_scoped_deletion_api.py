from __future__ import annotations

import json

import pytest
from fastapi.testclient import TestClient

import study_app.app as app_module
import study_app.store as store_module
from study_app.app import create_app

HEADERS = {"origin": "http://127.0.0.1", "x-study-csrf": "local"}


@pytest.mark.parametrize("kind", ["entry", "empty-folder", "subtree"])
def test_warm_delete_and_followup_reads_do_not_copy_or_revalidate_library(
    settings_factory, monkeypatch, kind,
):
    monkeypatch.setattr(app_module, "_pdf_export_available", lambda: False)
    app = create_app(settings_factory(), local_mode=True)
    store = app.state.store
    folder = store.create_folder("Algebra", "algebra", None)
    survivor = store.create_entry(folder["id"], "df", "Ring", "ring", "", "Surviving body")
    empty = store.create_folder("Empty", "empty", folder["id"])
    subtree = store.create_folder("Deleted", "deleted", folder["id"])
    child = store.create_folder("Child", "child", subtree["id"])
    target = store.create_entry(child["id"], "df", "Group", "group", "", "Deleted body")
    store.snapshot()
    store.search("body")
    app.state.review.stats()

    def forbidden(*args, **kwargs):
        pytest.fail("a warm deletion must not copy or fully validate the library")

    monkeypatch.setattr(store, "_begin_v2_transaction", forbidden)
    monkeypatch.setattr(store, "_read_v2", forbidden)
    monkeypatch.setattr(store_module, "validate_library", forbidden)
    monkeypatch.setattr(store_module.shutil, "copytree", forbidden)
    target_id = target["id"] if kind == "entry" else empty["id"] if kind == "empty-folder" else subtree["id"]
    endpoint = "entries" if kind == "entry" else "folders"
    with TestClient(app, base_url="http://127.0.0.1", client=("127.0.0.1", 50000)) as client:
        deleted = client.delete(
            f"/api/{endpoint}/{target_id}",
            params={"include_library": "false", "recursive": str(kind == "subtree").lower()},
            headers=HEADERS,
        )
        assert deleted.status_code == 200, deleted.text
        assert deleted.json()["ok"] is True
        bootstrap = client.get("/api/bootstrap?compact=true")
        assert bootstrap.status_code == 200, bootstrap.text
        assert target_id not in {item["id"] for item in bootstrap.json()[endpoint]}
        assert client.get(f"/api/entries/{survivor['id']}").status_code == 200
        search = client.get("/api/search", params={"q": "Surviving body"})
        assert search.status_code == 200, search.text
        assert store.pending_deletions() == {}


def test_scoped_delete_rejects_invalid_neighbor_edit_before_detaching(settings_factory):
    app = create_app(settings_factory(), local_mode=True)
    store = app.state.store
    folder = store.create_folder("Algebra", "algebra", None)
    target = store.create_entry(folder["id"], "df", "Group", "group", "", "Target body")
    survivor = store.create_entry(folder["id"], "df", "Ring", "ring", "", "Surviving body")
    store.snapshot()
    target_path = store.data_dir / target["formulations"][0]["file"]
    sidecar = (store.data_dir / survivor["formulations"][0]["file"]).parent / "_entry.json"
    metadata = json.loads(sidecar.read_text())
    metadata["title"] = ""
    sidecar.write_text(json.dumps(metadata))
    with TestClient(app, base_url="http://127.0.0.1", client=("127.0.0.1", 50000)) as client:
        result = client.delete(f"/api/entries/{target['id']}", headers=HEADERS)
    assert result.status_code == 422
    assert target_path.read_text() == "Target body\n"
    assert store.pending_deletions() == {}
