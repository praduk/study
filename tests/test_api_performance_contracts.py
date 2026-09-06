from __future__ import annotations

from fastapi.testclient import TestClient

import study_app.app as app_module
from study_app.app import create_app

LOCAL_HEADERS = {"origin": "http://127.0.0.1", "x-study-csrf": "local"}


def _client(app):
    return TestClient(
        app,
        base_url="http://127.0.0.1",
        client=("127.0.0.1", 50000),
    )


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
