from __future__ import annotations

import base64
import hashlib
import io
import sqlite3

from fastapi.testclient import TestClient
from PIL import Image

from study_app.app import create_app
from study_app.auth import COOKIE_NAME, make_password_hash


def _png(width: int = 4, height: int = 3) -> bytes:
    output = io.BytesIO()
    Image.new("RGB", (width, height), "#638b7d").save(output, "PNG")
    return output.getvalue()


def test_server_mode_enforces_host_origin_csrf_and_server_side_sessions(settings_factory):
    settings = settings_factory(password_hash=make_password_hash("correct horse battery staple"))
    app = create_app(settings, local_mode=False)
    with TestClient(
        app,
        base_url="http://study.test",
        client=("192.0.2.10", 50000),
    ) as client:
        assert client.get("/healthz", headers={"host": "evil.test"}).status_code == 400
        assert (
            client.post("/api/login", json={"password": "correct horse battery staple"}).status_code
            == 403
        )
        assert (
            client.post(
                "/api/login",
                json={"password": "correct horse battery staple"},
                headers={"origin": "http://evil.test"},
            ).status_code
            == 403
        )

        logged_in = client.post(
            "/api/login",
            json={"password": "correct horse battery staple"},
            headers={"origin": "http://study.test", "sec-fetch-site": "same-origin"},
        )
        assert logged_in.status_code == 200
        assert logged_in.headers["cache-control"] == "no-store"
        csrf = logged_in.json()["csrf"]
        token = client.cookies.get(COOKIE_NAME)
        assert token

        with sqlite3.connect(settings.data_dir / "runtime" / "sessions.sqlite3") as connection:
            stored = connection.execute("SELECT token_hash FROM sessions").fetchone()[0]
        assert token not in stored
        assert len(stored) == 64

        no_csrf = client.post(
            "/api/folders",
            json={"name": "Algebra", "slug": "algebra", "parent_id": None},
            headers={"origin": "http://study.test"},
        )
        assert no_csrf.status_code == 403
        created = client.post(
            "/api/folders",
            json={"name": "Algebra", "slug": "algebra", "parent_id": None},
            headers={"origin": "http://study.test", "x-study-csrf": csrf},
        )
        assert created.status_code == 200

        replacement = client.post(
            "/api/login",
            json={"password": "correct horse battery staple"},
            headers={"origin": "http://study.test"},
        )
        assert replacement.status_code == 200
        assert app.state.sessions.get(token) is None


def test_local_mode_rejects_non_loopback_clients_and_still_requires_csrf(settings_factory):
    settings = settings_factory()
    app = create_app(settings, local_mode=True)
    with TestClient(
        app,
        base_url="http://127.0.0.1",
        client=("127.0.0.1", 50000),
    ) as client:
        session = client.get("/api/session")
        assert session.status_code == 200
        assert session.json()["auth_required"] is False
        assert (
            client.post(
                "/api/folders",
                json={"name": "Analysis", "slug": "analysis", "parent_id": None},
                headers={"origin": "http://127.0.0.1"},
            ).status_code
            == 403
        )
        assert (
            client.post(
                "/api/folders",
                json={"name": "Analysis", "slug": "analysis", "parent_id": None},
                headers={"origin": "http://127.0.0.1", "x-study-csrf": "local"},
            ).status_code
            == 200
        )

    remote = TestClient(
        create_app(settings_factory(), local_mode=True),
        base_url="http://127.0.0.1",
        client=("192.0.2.10", 50000),
    )
    assert remote.get("/healthz").status_code == 403


def test_delete_api_requires_csrf_and_explicit_recursive_folder_confirmation(
    settings_factory,
):
    settings = settings_factory()
    app = create_app(settings, local_mode=True)
    headers = {"origin": "http://127.0.0.1", "x-study-csrf": "local"}
    with TestClient(
        app,
        base_url="http://127.0.0.1",
        client=("127.0.0.1", 50000),
    ) as client:
        folder = client.post(
            "/api/folders",
            json={"name": "Algebra", "slug": "algebra", "parent_id": None},
            headers=headers,
        ).json()
        entry = client.post(
            "/api/entries",
            json={
                "folder_id": folder["id"],
                "kind": "df",
                "title": "Group",
                "tag": "group",
                "header": "",
                "content": "A group.",
            },
            headers=headers,
        ).json()

        assert client.delete(f"/api/entries/{entry['id']}").status_code == 403
        refused = client.delete(f"/api/folders/{folder['id']}", headers=headers)
        assert refused.status_code == 422
        assert "confirm recursive deletion" in refused.json()["detail"]

        removed = client.delete(f"/api/entries/{entry['id']}", headers=headers)
        assert removed.status_code == 200
        assert removed.json()["deletion"]["entry_count"] == 1
        assert removed.json()["library"]["entries"] == []

        empty_folder = client.delete(f"/api/folders/{folder['id']}", headers=headers)
        assert empty_folder.status_code == 200
        assert empty_folder.json()["deletion"]["folder_count"] == 1
        assert empty_folder.json()["library"]["folders"] == []

        recursive_folder = client.post(
            "/api/folders",
            json={"name": "Topology", "slug": "topology", "parent_id": None},
            headers=headers,
        ).json()
        nested = client.post(
            "/api/folders",
            json={
                "name": "Point set",
                "slug": "point-set",
                "parent_id": recursive_folder["id"],
            },
            headers=headers,
        ).json()
        recursive = client.delete(
            f"/api/folders/{recursive_folder['id']}?recursive=true",
            headers=headers,
        )
        assert recursive.status_code == 200
        assert recursive.json()["deletion"]["folder_count"] == 2
        assert nested["id"] not in {
            folder["id"] for folder in recursive.json()["library"]["folders"]
        }


def test_csp_authorizes_exact_inline_bootstrap_scripts(settings_factory):
    settings = settings_factory(rich_frontend=True)
    settings.built_frontend.mkdir(parents=True)
    script_bodies = ("window.first = 1;", "\nwindow.second = '<tag>';\n")
    settings.built_frontend.joinpath("index.html").write_text(
        "<!doctype html><script>"
        + script_bodies[0]
        + "</script><script src='/assets/app.js'></script><script>"
        + script_bodies[1]
        + "</script>",
        encoding="utf-8",
    )
    app = create_app(settings, local_mode=True)
    with TestClient(
        app,
        base_url="http://127.0.0.1",
        client=("127.0.0.1", 50000),
    ) as client:
        policy = client.get("/").headers["content-security-policy"]

    script_policy = next(
        directive for directive in policy.split(";") if directive.strip().startswith("script-src ")
    )
    assert "'unsafe-inline'" not in script_policy
    for body in script_bodies:
        digest = base64.b64encode(hashlib.sha256(body.encode()).digest()).decode()
        assert f"'sha256-{digest}'" in script_policy


def test_csp_tracks_frontend_rebuild_without_server_restart(settings_factory):
    settings = settings_factory(rich_frontend=True)
    settings.built_frontend.mkdir(parents=True)
    index = settings.built_frontend / "index.html"
    old_body = "window.bootstrap = 'old';"
    new_body = "window.bootstrap = 'new';"
    index.write_text(f"<!doctype html><script>{old_body}</script>", encoding="utf-8")
    app = create_app(settings, local_mode=True)

    index.write_text(f"<!doctype html><script>{new_body}</script>", encoding="utf-8")
    with TestClient(
        app,
        base_url="http://127.0.0.1",
        client=("127.0.0.1", 50000),
    ) as client:
        response = client.get("/")

    old_digest = base64.b64encode(hashlib.sha256(old_body.encode()).digest()).decode()
    new_digest = base64.b64encode(hashlib.sha256(new_body.encode()).digest()).decode()
    script_policy = next(
        directive
        for directive in response.headers["content-security-policy"].split(";")
        if directive.strip().startswith("script-src ")
    )
    assert response.status_code == 200
    assert response.content == index.read_bytes()
    assert f"'sha256-{new_digest}'" in script_policy
    assert f"'sha256-{old_digest}'" not in script_policy


def test_canonical_library_path_serves_spa_without_capturing_reserved_routes(settings_factory):
    settings = settings_factory(rich_frontend=True)
    settings.built_frontend.mkdir(parents=True)
    index = settings.built_frontend / "index.html"
    index.write_text("<!doctype html><title>Study</title>", encoding="utf-8")
    app = create_app(settings, local_mode=True)

    with TestClient(
        app,
        base_url="http://127.0.0.1",
        client=("127.0.0.1", 50000),
    ) as client:
        response = client.get("/library/math/algebra/th/lagrange/pf")
        missing_api = client.get("/api/not-a-route")
        missing_media = client.get("/media/not-a-file")

    assert response.status_code == 200
    assert response.content == index.read_bytes()
    assert response.headers["cache-control"] == "no-cache"
    assert "content-security-policy" in response.headers
    assert missing_api.status_code == 404
    assert missing_media.status_code == 404


def test_image_upload_normalizes_and_rejects_unapproved_formats(settings_factory):
    settings = settings_factory(max_image_megapixels=1)
    app = create_app(settings, local_mode=True)
    headers = {"origin": "http://127.0.0.1", "x-study-csrf": "local"}
    with TestClient(
        app,
        base_url="http://127.0.0.1",
        client=("127.0.0.1", 50000),
    ) as client:
        folder = client.post(
            "/api/folders",
            json={"name": "Topology", "slug": "topology", "parent_id": None},
            headers=headers,
        ).json()
        entry = client.post(
            "/api/entries",
            json={
                "folder_id": folder["id"],
                "kind": "df",
                "title": "Open set",
                "tag": "open-set",
                "header": "",
                "content": "Body",
            },
            headers=headers,
        ).json()
        assert entry["review_modes"] == ["statement"]
        uploaded = client.post(
            f"/api/entries/{entry['id']}/images",
            files={"image": ("paste.png", _png(), "image/png")},
            data={"alt": "bad](/not-an-image)", "width": "43", "invert_lightness": "true"},
            headers=headers,
        )
        assert uploaded.status_code == 200
        value = uploaded.json()
        assert value["path"].endswith(".png")
        assert value["pixels"] == [4, 3]
        assert "bad\\](/not-an-image)" in value["markdown"]
        media = client.get("/" + value["path"])
        assert media.status_code == 200
        assert media.headers["content-type"] == "image/png"

        bitmap = io.BytesIO()
        Image.new("RGB", (3, 3)).save(bitmap, "BMP")
        rejected = client.post(
            f"/api/entries/{entry['id']}/images",
            files={"image": ("image.bmp", bitmap.getvalue(), "image/bmp")},
            headers=headers,
        )
        assert rejected.status_code == 415

        too_many_pixels = client.post(
            f"/api/entries/{entry['id']}/images",
            files={"image": ("large.png", _png(1001, 1000), "image/png")},
            headers=headers,
        )
        assert too_many_pixels.status_code == 413

        outside = settings.root / "outside.png"
        outside.write_bytes(_png())
        unsafe_name = "a" * 64 + ".png"
        (settings.data_dir / "media" / unsafe_name).symlink_to(outside)
        assert client.get(f"/media/{unsafe_name}").status_code == 404
