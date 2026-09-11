from __future__ import annotations

import asyncio
import json
import socket
import threading

import pytest
import uvicorn

from study_app.app import create_app


def test_packaged_entry_review_controls_desktop_and_phone(settings_factory, tmp_path):
    playwright_api = pytest.importorskip("playwright.async_api")
    app = create_app(settings_factory(), local_mode=True)
    store = app.state.store
    folder = store.create_folder("Algebra", "algebra", None)
    entry = store.create_entry(folder["id"], "df", "Group", "group", "", "Definition")
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
            page = await browser.new_page(viewport={"width": 1440, "height": 1000})
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            expect = playwright_api.expect
            try:
                await page.goto(f"http://127.0.0.1:{port}/library/algebra/df/group")
                control = page.get_by_role("checkbox", name="Include this item in review")
                tree_control = page.get_by_role("checkbox", name="Include Group in review")
                due = page.get_by_role("button", name="Start review, 1 due")
                await expect(control).to_be_checked()
                await expect(due).to_be_enabled()
                await tree_control.click()
                await expect(control).not_to_be_checked()
                await expect(page.get_by_role("button", name="Start review, 0 due")).to_be_enabled()
                assert store.get_entry(entry["id"])["review_enabled"] is False
                await page.reload()
                await expect(control).not_to_be_checked()
                await control.focus()
                await page.keyboard.press("Space")
                await expect(due).to_be_enabled()
                await expect(tree_control).to_be_checked()
                await page.get_by_role("checkbox", name="Include Algebra in review").click()
                await expect(page.get_by_text("Paused by folder: Algebra", exact=True)).to_be_visible()
                await expect(control).to_be_checked()
                await expect(page.get_by_role("button", name="Start review, 0 due")).to_be_enabled()
                await page.get_by_role("checkbox", name="Include Algebra in review").click()
                await expect(due).to_be_enabled()

                async def fail_save(route):
                    await route.fulfill(status=503, content_type="application/json",
                                        body=json.dumps({"detail": "Simulated preference failure"}))

                route_pattern = "**/api/entries/*?include_review_stats=true"
                await page.route(route_pattern, fail_save)
                await control.click()
                await expect(page.locator(".toast-error")).to_contain_text("Simulated preference failure")
                await expect(control).to_be_checked()
                await expect(control).to_be_enabled()
                await page.unroute(route_pattern, fail_save)
                await page.locator(".toast-error").click()
                await page.screenshot(path=str(tmp_path / "desktop-review.png"))

                await page.get_by_role("button", name="Toggle dark mode").click()
                await page.set_viewport_size({"width": 390, "height": 844})
                await expect(control).to_be_visible()
                await expect(page.get_by_role("button", name="Edit", exact=True)).to_be_hidden()
                await control.click()
                await expect(page.get_by_text("Excluded from review", exact=True)).to_be_visible()
                await expect(control).to_be_enabled()
                assert store.get_entry(entry["id"])["review_enabled"] is False
                await page.reload()
                await expect(control).not_to_be_checked()
                await control.click()
                await expect(page.get_by_text("Included in review", exact=True)).to_be_visible()
                await expect(control).to_be_enabled()
                assert store.get_entry(entry["id"])["review_enabled"] is True
                assert await page.evaluate("document.documentElement.scrollWidth <= innerWidth")
                await page.screenshot(path=str(tmp_path / "phone-review.png"))
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
