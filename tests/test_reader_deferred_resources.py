from __future__ import annotations

import asyncio
import socket
import threading
from urllib.parse import parse_qs, urlsplit

import pytest
import uvicorn

from study_app.app import create_app


def test_reader_defers_math_previews_and_linked_items_until_needed(settings_factory):
    playwright_api = pytest.importorskip("playwright.async_api")
    app = create_app(settings_factory(), local_mode=True)
    store = app.state.store
    folder = store.create_folder("Deferred reading", "deferred-reading", None)
    theorem = store.create_entry(
        folder["id"], "th", "Theorem fixture", "fixture", "",
        "Read @target.\n\n" + "A paragraph of ordinary prose.\n\n" * 75,
    )
    store.add_supplement(theorem["id"], {
        "kind": "pf", "label": "Main proof", "main": True, "content": "Main proof in prose.",
    })
    store.add_supplement(theorem["id"], {
        "kind": "pf", "label": "Alternative proof", "main": False, "subtag": "alternative",
        "content": "Alternative proof with $x^2$.",
    })
    store.create_entry(folder["id"], "df", "Preview target", "target", "", "Preview body with $y^2$.")
    store.create_entry(folder["id"], "rk", "Incoming link", "incoming-link", "", "See @fixture.")

    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    server = uvicorn.Server(uvicorn.Config(app, log_level="error", ws="none"))
    thread = threading.Thread(target=server.run, kwargs={"sockets": [sock]}, daemon=True)

    async def exercise():
        for _ in range(500):
            if server.started:
                break
            await asyncio.sleep(0.01)
        assert server.started
        async with playwright_api.async_playwright() as playwright:
            try:
                browser = await playwright.chromium.launch()
            except playwright_api.Error as exc:
                if "Executable doesn't exist" in str(exc):
                    pytest.skip("Playwright Chromium is not installed")
                raise
            page = await browser.new_page(viewport={"width": 1440, "height": 900})
            expect = playwright_api.expect
            requests = []
            errors = []
            page.on("request", lambda request: requests.append(urlsplit(request.url)))
            page.on("pageerror", lambda error: errors.append(str(error)))
            url = f"http://127.0.0.1:{port}/library/deferred-reading/th/fixture"
            try:
                await page.goto(url)
                trigger = page.locator('.reading-pane [data-study-reference-status="resolved"]')
                await expect(trigger).to_have_text("Preview target")
                await expect(page.get_by_text("Alternative proof with", exact=False)).to_have_count(0)
                assert not any(request.path.startswith("/vendor/mathjax/") for request in requests)
                assert not any(request.path.endswith("/linked-items") for request in requests)
                assert not any(request.path == "/api/references/resolve" for request in requests)
                batch = [request for request in requests if request.path == "/api/references/resolve-batch"]
                assert len(batch) == 1 and parse_qs(batch[0].query)["preview"] == ["false"]

                await trigger.hover()
                popup = page.locator(".reference-preview-popover")
                await expect(popup).to_contain_text("Preview body with")
                await expect(popup.locator("mjx-container svg")).to_be_visible()
                assert sum(request.path == "/api/references/resolve" for request in requests) == 1
                await popup.get_by_role("button", name="Open entry").click()
                await expect(page.get_by_role("heading", name="Preview target")).to_be_visible()
                await page.go_back()
                await expect(page.get_by_role("heading", name="Theorem fixture")).to_be_visible()
                await page.go_forward()
                await expect(page.get_by_role("heading", name="Preview target")).to_be_visible()
                await page.go_back()
                await expect(page.get_by_role("heading", name="Theorem fixture")).to_be_visible()

                links = page.locator(".linked-items")
                await links.scroll_into_view_if_needed()
                await expect(links.get_by_role("link", name="Incoming link", exact=False)).to_be_visible()
                proof = page.locator(".supplement-list details").filter(has_text="Alternative proof")
                await proof.locator("summary").click()
                await expect(proof.locator("mjx-container svg")).to_be_visible()
                await proof.locator("summary").click()
                await expect(proof.locator("mjx-container svg")).not_to_be_visible()
                await proof.locator("summary").click()
                await expect(proof.locator("mjx-container svg")).to_be_visible()
                await page.goto(f"{url}/pf/alternative")
                await expect(proof.locator("mjx-container svg")).to_be_visible()
                await expect(page.locator(".supplement-list details[open]")).to_have_count(1)
                assert errors == []
            finally:
                await browser.close()

    thread.start()
    try:
        asyncio.run(exercise())
    finally:
        server.should_exit = True
        thread.join(timeout=5)
        sock.close()
