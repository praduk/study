from __future__ import annotations

import asyncio
import json
import socket
import threading

import pytest
import uvicorn

from study_app.app import create_app


async def _vim_command(page, command: str) -> None:
    editor = page.locator(".editor-dialog .cm-content")
    await editor.press("Escape")
    await editor.press(":")
    await page.keyboard.type(command)
    await page.keyboard.press("Enter")


def test_packaged_editor_waits_for_all_saves_and_keeps_failed_drafts(settings_factory):
    """A failed variant must not unlock a retry while another write is pending."""
    playwright_api = pytest.importorskip("playwright.async_api")
    settings = settings_factory()
    app = create_app(settings, local_mode=True)
    store = app.state.store
    folder = store.create_folder("Editor saves", "editor-saves", None)
    entry = store.create_entry(
        folder["id"], "df", "Save regression", "save-regression", "", "Original main"
    )
    entry = store.add_formulation(
        entry["id"],
        {"label": "Other", "subtag": "other", "content": "Original alternative"},
    )
    entry_id = entry["id"]
    main_id, other_id = (variant["id"] for variant in entry["formulations"])
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    server = uvicorn.Server(uvicorn.Config(app, log_level="error", ws="none"))
    thread = threading.Thread(target=server.run, kwargs={"sockets": [sock]}, daemon=True)

    async def exercise() -> None:
        for _ in range(500):
            if server.started:
                break
            await asyncio.sleep(0.01)
        assert server.started, "temporary Study server did not start"
        async with playwright_api.async_playwright() as playwright:
            try:
                browser = await playwright.chromium.launch()
            except playwright_api.Error as exc:
                if "Executable doesn't exist" in str(exc):
                    pytest.skip("Playwright Chromium is not installed")
                raise
            page = await browser.new_page(viewport={"width": 1440, "height": 1000})
            errors: list[str] = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            held = asyncio.Event()
            release = asyncio.Event()
            failed = asyncio.Event()

            async def intercept(route) -> None:
                if route.request.url.endswith(f"/{main_id}"):
                    await route.fulfill(
                        status=503,
                        content_type="application/json",
                        body=json.dumps({"detail": "Simulated save failure"}),
                    )
                    failed.set()
                elif route.request.url.endswith(f"/{other_id}"):
                    held.set()
                    await release.wait()
                    await route.continue_()
                else:
                    await route.continue_()

            try:
                await page.goto(
                    f"http://127.0.0.1:{port}/library/editor-saves/df/save-regression"
                )
                await page.get_by_role("button", name="Edit", exact=True).click()
                editor = page.locator(".editor-dialog .cm-content")
                dialog = page.locator(".editor-dialog")
                expect = playwright_api.expect
                await expect(dialog).to_be_visible()
                await dialog.get_by_role("button", name="Other", exact=True).click()
                await editor.fill("Changed alternative that is held in flight")
                await dialog.get_by_role("button", name="Main · main", exact=True).click()
                await editor.fill("Draft that must survive failure")
                await page.get_by_label("Title", exact=True).fill("Partially saved title")
                await page.get_by_label("Tag", exact=True).fill("partially-saved-tag")
                await page.route("**/api/entries/*/content/*", intercept)
                await _vim_command(page, "wq")
                await asyncio.wait_for(held.wait(), timeout=10)
                await asyncio.wait_for(failed.wait(), timeout=10)
                # Let the failed request reach the save handler while the other
                # request is deliberately unresolved. A fail-fast Promise.all
                # unlocks the editor here and permits overlapping retries.
                await page.wait_for_timeout(200)
                await expect(dialog).to_have_attribute("aria-busy", "true")
                await expect(editor).to_have_attribute("contenteditable", "false")
                controls = dialog.locator(
                    ".editor-metadata input, .editor-metadata select, "
                    ".editor-metadata textarea, .variant-tabs button, .variant-actions button"
                )
                for control in await controls.all():
                    await expect(control).to_be_disabled()
                cancel = page.get_by_role("button", name="Cancel", exact=True)
                await expect(cancel).to_be_disabled()
                await expect(dialog.get_by_role("button", name="Close", exact=True)).to_have_count(0)
                await cancel.click(force=True)
                await _vim_command(page, "q")
                await page.keyboard.press("Escape")
                await page.mouse.click(1, 1)
                await expect(dialog).to_be_visible()
                await editor.press("i")
                await page.keyboard.type("This must not change the saved snapshot")
                assert await editor.inner_text() == "Draft that must survive failure"

                release.set()
                await expect(page.get_by_role("alert")).to_have_text("Simulated save failure")
                await expect(dialog).to_be_visible()
                await expect(editor).to_have_attribute("contenteditable", "true")
                await expect(page.get_by_label("Title", exact=True)).to_be_enabled()
                await expect(cancel).to_be_enabled()
                assert await editor.inner_text() == "Draft that must survive failure"
                assert store.get_entry(entry_id)["formulations"][0]["content"] == "Original main\n"
                assert store.get_entry(entry_id)["title"] == "Partially saved title"
                assert store.get_entry(entry_id)["tag"] == "partially-saved-tag"
                await page.unroute("**/api/entries/*/content/*", intercept)
                # Reverting metadata after a partial save must still write that
                # intended value, although it equals the editor's old baseline.
                await page.get_by_label("Title", exact=True).fill("Save regression")
                await page.get_by_label("Tag", exact=True).fill("save-regression")
                await editor.fill("Retry saves the retained draft")
                await _vim_command(page, "wq")
                await expect(dialog).to_have_count(0)
                assert store.get_entry(entry_id)["formulations"][0]["content"] == (
                    "Retry saves the retained draft\n"
                )
                assert store.get_entry(entry_id)["title"] == "Save regression"
                assert store.get_entry(entry_id)["tag"] == "save-regression"
                assert errors == []
            finally:
                release.set()
                await browser.close()

    thread.start()
    try:
        asyncio.run(exercise())
    finally:
        server.should_exit = True
        thread.join(timeout=5)
        sock.close()
