from __future__ import annotations

import asyncio
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

import pytest
from fastapi.testclient import TestClient

import study_app.app as app_module
from study_app.app import create_app
from study_app.export import export_pdf
from study_app.store import StoreError

LOCAL_HEADERS = {"origin": "http://127.0.0.1", "x-study-csrf": "local"}


class _InitialAssetParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.paths: set[str] = set()

    def handle_starttag(self, _tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for name, value in attrs:
            if name in {"src", "href"} and value and value.startswith("/"):
                self.paths.add(value)


def _client(app):
    return TestClient(
        app,
        base_url="http://127.0.0.1",
        client=("127.0.0.1", 50000),
    )


def test_complete_packaged_frontend_runs_without_a_frontend_build(settings_factory):
    settings = settings_factory()

    with _client(create_app(settings, local_mode=True)) as client:
        index = client.get("/")
        mathjax = client.get("/vendor/mathjax/tex-svg.js")
        deep_link = client.get("/library/algebra/df/group")

    assert index.status_code == 200
    assert "Study — mathematical recall" in index.text
    assert "/_next/static/" in index.text
    assert "no-build UI" not in index.text
    assert index.headers["cache-control"] == "no-cache"
    assert "default-src 'self'" in index.headers["content-security-policy"]
    assert mathjax.status_code == 200
    assert len(mathjax.content) > 100_000
    assert deep_link.status_code == 200
    assert "Study — mathematical recall" in deep_link.text


def test_every_initial_frontend_asset_is_shipped(settings_factory):
    settings = settings_factory()
    with _client(create_app(settings, local_mode=True)) as client:
        index = client.get("/")
        parser = _InitialAssetParser()
        parser.feed(index.text)
        responses = {path: client.get(path) for path in parser.paths}

    assert parser.paths
    assert "/vendor/excalidraw/index.css" not in parser.paths
    assert all(
        (settings.frontend_public / path.removeprefix("/").split("?", 1)[0]).is_file()
        for path in parser.paths
    )
    assert all(response.status_code == 200 for response in responses.values())
    assert all(
        not response.headers.get("content-type", "").startswith("text/html")
        for response in responses.values()
    )


def test_static_revalidation_returns_no_body_for_unchanged_vendor_asset(settings_factory):
    with _client(create_app(settings_factory(), local_mode=True)) as client:
        asset = client.get("/vendor/excalidraw/index.css")
        etag = asset.headers["etag"]
        unchanged = client.get("/vendor/excalidraw/index.css", headers={"if-none-match": f'"old", W/{etag}'})
        changed = client.get("/vendor/excalidraw/index.css", headers={"if-none-match": '"old"'})
    assert unchanged.status_code == 304
    assert unchanged.content == b""
    assert unchanged.headers["etag"] == etag
    assert changed.status_code == 200
    assert changed.content == asset.content


def test_static_brotli_respects_encoding_weights_validators_and_ranges(settings_factory):
    settings = settings_factory()
    url = "/vendor/mathjax/tex-svg.js"
    source = settings.frontend_public / url.lstrip("/")
    compressed = source.with_suffix(".js.br").read_bytes()
    with _client(create_app(settings, local_mode=True)) as client:
        with client.stream("GET", url, headers=[("accept-encoding", "gzip"), ("accept-encoding", "br")]) as brotli:
            assert brotli.status_code == 200
            assert brotli.headers["content-encoding"] == "br"
            assert brotli.headers["content-type"].split(";")[0] in {"application/javascript", "text/javascript"}
            assert brotli.headers["vary"] == "Accept-Encoding"
            assert b"".join(brotli.iter_raw()) == compressed
            tag = brotli.headers["etag"]

        unchanged = client.get(url, headers={"accept-encoding": "br", "if-none-match": tag})
        assert unchanged.status_code == 304
        assert unchanged.headers["vary"] == "Accept-Encoding"
        assert not unchanged.content

        gzip = client.get(url, headers={"accept-encoding": "br;q=0.2, GZip;q=0.7", "if-none-match": tag})
        assert gzip.status_code == 200
        assert gzip.headers["content-encoding"] == "gzip"
        assert gzip.content == source.read_bytes()

        unchanged_gzip = client.get(url, headers={"accept-encoding": "gzip", "if-none-match": gzip.headers["etag"]})
        assert unchanged_gzip.status_code == 304
        assert unchanged_gzip.headers["vary"] == "Accept-Encoding"

        identity = client.get(url, headers={
            "accept-encoding": "br;q=0.4, gzip;q=0, identity;q=0.9",
            "if-none-match": gzip.headers["etag"],
        })
        assert identity.status_code == 200
        assert "content-encoding" not in identity.headers
        assert identity.headers["vary"] == "Accept-Encoding"
        assert len({identity.headers["etag"], gzip.headers["etag"], tag}) == 3

        partial = client.get(url, headers={"accept-encoding": "br, gzip", "range": "bytes=0-19"})
        assert partial.status_code == 206
        assert "content-encoding" not in partial.headers
        assert partial.content == identity.content[:20]


def test_every_local_css_asset_is_shipped(settings_factory):
    public = settings_factory().frontend_public
    missing: list[tuple[Path, str]] = []
    for stylesheet in public.rglob("*.css"):
        for raw in re.findall(r"url\(([^)]+)\)", stylesheet.read_text(encoding="utf-8")):
            authored = raw.strip().strip("\"'")
            parsed = urlsplit(authored)
            if parsed.scheme or authored.startswith(("data:", "#")):
                continue
            pathname = unquote(parsed.path)
            target = (
                public / pathname.removeprefix("/")
                if pathname.startswith("/")
                else stylesheet.parent / pathname
            )
            resolved = target.resolve()
            if not resolved.is_relative_to(public.resolve()) or not resolved.is_file():
                missing.append((stylesheet.relative_to(public), authored))

    assert missing == []


def test_bootstrap_hides_pdf_capability_without_optional_dependency(
    settings_factory, monkeypatch
):
    monkeypatch.setattr(app_module, "_pdf_export_available", lambda: False)

    with _client(create_app(settings_factory(), local_mode=True)) as client:
        payload = client.get("/api/bootstrap").json()
        export = client.post("/api/export/pdf", json={}, headers=LOCAL_HEADERS)

    assert payload["capabilities"]["pdf_export"] is False
    assert export.status_code == 503


def test_static_lookup_cannot_escape_its_directory(settings_factory):
    with _client(create_app(settings_factory(), local_mode=True)) as client:
        response = client.get("/%2e%2e/pyproject.toml")
        missing_chunk = client.get("/_next/static/chunks/definitely-missing.js")
        missing_font = client.get("/vendor/excalidraw/missing.woff2")

    assert response.status_code == 404
    assert "[build-system]" not in response.text
    assert missing_chunk.status_code == 404
    assert missing_font.status_code == 404


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
    mathjax = settings.frontend_public / "vendor" / "mathjax" / "tex-svg.js"

    try:
        target = asyncio.run(
            export_pdf(
                app.state.store,
                app.state.store.ordered_entries(),
                "Offline export",
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
