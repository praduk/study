from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

import study_app.app as app_module
from study_app.app import create_app

LOCAL_HEADERS = {"origin": "http://127.0.0.1", "x-study-csrf": "local"}


def test_navigation_bootstrap_keeps_links_and_stats_without_editor_metadata(settings_factory):
    app = create_app(settings_factory(), local_mode=True)
    store = app.state.store
    folder = store.create_folder("Algebra", "algebra", None)
    entry = store.create_entry(folder["id"], "th", "Theorem", "theorem", "A long header", "Body")
    store.add_formulation(entry["id"], {"label": "Alternative", "subtag": "alt", "content": "Alternative body"})
    store.add_supplement(entry["id"], {"kind": "pf", "label": "Proof", "content": "Proof body"})
    with _client(app) as client:
        full = client.get("/api/bootstrap?compact=true").json()
        small = client.get("/api/bootstrap?navigation=true").json()
        detail = client.get(f"/api/entries/{entry['id']}").json()
    assert "tree" not in small
    assert small["review"] == full["review"]
    assert small["folders"] == full["folders"]
    summary = small["entries"][0]
    assert summary["canonical_tag"] == "algebra:th:theorem"
    assert "header" not in summary and "assets" not in summary
    for group in ("formulations", "supplements"):
        assert summary[group] == [{key: variant[key] for key in ("id", "main", "subtag", "kind") if key in variant}
                                  for variant in full["entries"][0][group]]
        assert all("file" not in variant and "content" not in variant for variant in summary[group])
    assert detail["header"] == "A long header"
    assert detail["formulations"][0]["content"] == "Body\n"


def test_interactive_authored_writes_do_not_back_up_the_whole_library(settings_factory, monkeypatch):
    app = create_app(settings_factory(), local_mode=True)
    store = app.state.store

    def forbidden():
        pytest.fail("interactive writes must not copy the whole library for rollback")

    monkeypatch.setattr(store, "_begin_v2_transaction", forbidden)
    folder = store.create_folder("Algebra", "algebra", None)
    entry = store.create_entry(folder["id"], "th", "Theorem", "theorem", "", "Body")
    store.add_formulation(entry["id"], {"label": "Alternative", "subtag": "alt", "content": "Alternative"})
    store.add_supplement(entry["id"], {"kind": "pf", "label": "Proof", "content": "Proof"})
    store.update_entry(entry["id"], {"tag": "new-tag"})
    store.update_folder(folder["id"], {"slug": "groups"})
    assert store.get_entry(entry["id"])["canonical_tag"] == "groups:th:new-tag"
    assert store.check_data()["entries"] == 1


def _client(app):
    return TestClient(
        app,
        base_url="http://127.0.0.1",
        client=("127.0.0.1", 50000),
    )


@pytest.mark.parametrize("item_type", ["entries", "folders"])
def test_delete_can_omit_discarded_library_without_building_tree(
    settings_factory, monkeypatch, item_type,
):
    app = create_app(settings_factory(), local_mode=True)
    store = app.state.store
    folder = store.create_folder("Algebra", "algebra", None)
    entry = store.create_entry(folder["id"], "df", "Group", "group", "", "Definition")
    survivor = store.create_entry(folder["id"], "df", "Ring", "ring", "", "Definition")
    empty_folder = store.create_folder("Empty", "empty", None)
    item_id = entry["id"] if item_type == "entries" else empty_folder["id"]

    def unexpected_tree(*args, **kwargs):
        raise AssertionError("omitted deletion library must not construct a nested tree")

    monkeypatch.setattr(store, "_tree", unexpected_tree)
    with _client(app) as client:
        response = client.delete(
            f"/api/{item_type}/{item_id}?include_library=false", headers=LOCAL_HEADERS,
        )
        refreshed = client.get("/api/bootstrap?compact=true")

    assert response.status_code == 200
    assert set(response.json()) == {"ok", "deletion", "review_cleanup"}
    assert response.json()["ok"] is True
    assert refreshed.status_code == 200
    assert survivor["id"] in {entry["id"] for entry in refreshed.json()["entries"]}
    assert item_id not in {item["id"] for item in refreshed.json()[item_type]}


def test_compact_bootstrap_omits_only_the_derived_tree(settings_factory, monkeypatch):
    monkeypatch.setattr(app_module, "_pdf_export_available", lambda: False)
    app = create_app(settings_factory(), local_mode=True)
    folder = app.state.store.create_folder("Algebra", "algebra", None)
    app.state.store.create_entry(
        folder["id"], "df", "Group", "group", "", "A set with an operation."
    )

    with _client(app) as client:
        full = client.get("/api/bootstrap")
        compact = client.get("/api/bootstrap", params={"compact": "true"})

    assert full.status_code == 200
    assert compact.status_code == 200
    full_payload = full.json()
    compact_payload = compact.json()
    assert full_payload["tree"]
    assert "tree" not in compact_payload
    assert {
        key: value for key, value in full_payload.items() if key != "tree"
    } == compact_payload


def test_compact_bootstrap_does_not_construct_discarded_tree(settings_factory, monkeypatch):
    app = create_app(settings_factory(), local_mode=True)
    folder = app.state.store.create_folder("Algebra", "algebra", None)
    app.state.store.create_entry(folder["id"], "df", "Group", "group", "", "Definition")

    def unexpected_tree(*args, **kwargs):
        raise AssertionError("compact bootstrap must not construct the nested library tree")

    monkeypatch.setattr(app.state.store, "_tree", unexpected_tree)
    with _client(app) as client:
        response = client.get("/api/bootstrap?compact=true")
    assert response.status_code == 200
    assert len(response.json()["entries"]) == 1


def test_folder_patch_keeps_the_legacy_response_unless_review_stats_are_requested(
    settings_factory,
):
    app = create_app(settings_factory(), local_mode=True)
    folder = app.state.store.create_folder("Algebra", "algebra", None)
    app.state.store.create_entry(
        folder["id"], "df", "Group", "group", "", "A set with an operation."
    )

    with _client(app) as client:
        legacy = client.patch(
            f"/api/folders/{folder['id']}",
            json={"review_enabled": False},
            headers=LOCAL_HEADERS,
        )
        enriched = client.patch(
            f"/api/folders/{folder['id']}",
            params={"include_review_stats": "true"},
            json={"review_enabled": True},
            headers=LOCAL_HEADERS,
        )

    assert legacy.status_code == 200
    assert legacy.json()["id"] == folder["id"]
    assert legacy.json()["review_enabled"] is False
    assert "folder" not in legacy.json()
    assert "review" not in legacy.json()

    assert enriched.status_code == 200
    assert set(enriched.json()) == {"folder", "review", "git"}
    assert enriched.json()["folder"]["id"] == folder["id"]
    assert enriched.json()["folder"]["review_enabled"] is True
    assert enriched.json()["review"]["due"] == 1


def test_large_bootstrap_responses_are_gzip_compressed(settings_factory, monkeypatch):
    monkeypatch.setattr(app_module, "_pdf_export_available", lambda: False)
    app = create_app(settings_factory(), local_mode=True)
    folder = app.state.store.create_folder("Algebra", "algebra", None)
    app.state.store.create_entry(
        folder["id"],
        "df",
        "Group",
        "group",
        "context " * 400,
        "A set with an operation.",
    )

    with _client(app) as client:
        identity = client.get(
            "/api/bootstrap",
            params={"compact": "true"},
            headers={"accept-encoding": "identity"},
        )
        compressed = client.get(
            "/api/bootstrap",
            params={"compact": "true"},
            headers={"accept-encoding": "gzip"},
        )

    assert identity.status_code == 200
    assert compressed.status_code == 200
    assert "content-encoding" not in identity.headers
    assert compressed.headers["content-encoding"] == "gzip"
    assert compressed.json() == identity.json()
    assert int(compressed.headers["content-length"]) < int(
        identity.headers["content-length"]
    )


def test_static_assets_receive_lifetime_appropriate_cache_headers(settings_factory):
    settings = settings_factory()
    static_root = settings.frontend_public / "_next" / "static"
    next_asset = next(path for path in static_root.rglob("*") if path.is_file())
    next_url = f"/{next_asset.relative_to(settings.frontend_public).as_posix()}"

    with _client(create_app(settings, local_mode=True)) as client:
        html = client.get("/")
        hashed = client.get(next_url)
        vendor = client.get("/vendor/mathjax/tex-svg.js")

    assert html.status_code == 200
    assert html.headers["cache-control"] == "no-cache"
    assert hashed.status_code == 200
    assert hashed.headers["cache-control"] == "private, max-age=31536000, immutable"
    assert vendor.status_code == 200
    assert vendor.headers["cache-control"] == "private, max-age=3600"


def test_precompressed_assets_and_byte_ranges_are_not_gzipped(settings_factory):
    settings = settings_factory()
    font = next(settings.frontend_public.rglob("*.woff2"))
    url = f"/{font.relative_to(settings.frontend_public).as_posix()}"

    with _client(create_app(settings, local_mode=True)) as client:
        whole = client.get(url, headers={"accept-encoding": "gzip"})
        ranged = client.get(
            url,
            headers={"accept-encoding": "gzip", "range": "bytes=0-1999"},
        )

    assert whole.status_code == 200
    assert "content-encoding" not in whole.headers
    assert ranged.status_code == 206
    assert "content-encoding" not in ranged.headers
    assert ranged.headers["content-range"].startswith("bytes 0-1999/")
    assert len(ranged.content) == 2000
