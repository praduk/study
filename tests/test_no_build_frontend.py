from __future__ import annotations

import asyncio
from dataclasses import replace

import pytest
from fastapi.testclient import TestClient

import study_app.app as app_module
from study_app.app import create_app
from study_app.export import export_pdf
from study_app.store import StoreError

LOCAL_HEADERS = {"origin": "http://127.0.0.1", "x-study-csrf": "local"}


def _client(app):
    return TestClient(
        app,
        base_url="http://127.0.0.1",
        client=("127.0.0.1", 50000),
    )


def test_packaged_frontend_runs_when_compiled_frontend_is_absent(settings_factory):
    settings = settings_factory()
    assert not settings.built_frontend.exists()

    with _client(create_app(settings, local_mode=True)) as client:
        index = client.get("/")
        script = client.get("/app.js")
        stylesheet = client.get("/app.css")
        mathjax = client.get("/vendor/mathjax/tex-chtml.js")
        library_route = client.get("/library/algebra/df/group")

    assert index.status_code == 200
    assert "no-build UI" in index.text
    assert index.headers["cache-control"] == "no-cache"
    assert "default-src 'self'" in index.headers["content-security-policy"]
    assert script.status_code == 200
    assert "javascript" in script.headers["content-type"]
    assert stylesheet.status_code == 200
    assert stylesheet.headers["content-type"].startswith("text/css")
    assert mathjax.status_code == 200
    assert len(mathjax.content) > 100_000
    assert library_route.status_code == 200
    assert "no-build UI" in library_route.text


def test_compiled_frontend_requires_explicit_opt_in(settings_factory):
    settings = settings_factory()
    settings.built_frontend.mkdir(parents=True)
    (settings.built_frontend / "index.html").write_text(
        "<!doctype html><title>Rich Study</title>", encoding="utf-8"
    )

    with _client(create_app(settings, local_mode=True)) as client:
        default_response = client.get("/")
    with _client(create_app(replace(settings, rich_frontend=True), local_mode=True)) as client:
        rich_response = client.get("/")

    assert "no-build UI" in default_response.text
    assert "Rich Study" in rich_response.text


def test_bootstrap_hides_pdf_capability_without_optional_dependency(
    settings_factory, monkeypatch
):
    monkeypatch.setattr(app_module, "_pdf_export_available", lambda: False)

    with _client(create_app(settings_factory(), local_mode=True)) as client:
        payload = client.get("/api/bootstrap").json()

    assert payload["capabilities"]["pdf_export"] is False


def test_markdown_render_endpoint_escapes_html_and_decorates_safe_media(
    settings_factory,
):
    source = """<img src=x onerror=alert(1)>

$x^2$

![Graph](/media/aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.png#width=120&invert=lightness)
"""
    with _client(create_app(settings_factory(), local_mode=True)) as client:
        response = client.post(
            "/api/render/markdown",
            json={"source": source},
            headers=LOCAL_HEADERS,
        )

    assert response.status_code == 200
    rendered = response.json()["html"]
    assert "<img src=x onerror=" not in rendered
    assert "&lt;img src=x onerror=alert(1)&gt;" in rendered
    assert r"\(x^2\)" in rendered
    assert 'class="content-image invert-lightness"' in rendered
    assert 'style="width:100%"' in rendered


def test_fallback_static_lookup_cannot_escape_its_directory(settings_factory):
    with _client(create_app(settings_factory(), local_mode=True)) as client:
        response = client.get("/%2e%2e/pyproject.toml")

    assert response.status_code == 200
    assert "no-build UI" in response.text
    assert "[build-system]" not in response.text


def test_packaged_mathjax_supports_offline_pdf_export(settings_factory):
    settings = settings_factory()
    app = create_app(settings, local_mode=True)
    folder = app.state.store.create_folder("Algebra", "algebra", None)
    app.state.store.create_entry(
        folder["id"],
        "df",
        "Group",
        "group",
        "",
        r"A **group** with $x^2 \in \mathbb{R}$.",
    )
    mathjax = settings.no_build_frontend / "vendor" / "mathjax" / "tex-chtml.js"

    try:
        target = asyncio.run(
            export_pdf(
                app.state.store,
                app.state.store.ordered_entries(),
                "No-build export",
                True,
                mathjax,
            )
        )
    except StoreError as exc:
        if "Executable doesn't exist" in str(exc):
            pytest.skip("Playwright Chromium is not installed")
        raise

    assert target.read_bytes().startswith(b"%PDF-")
    assert target.stat().st_size > 1_000
