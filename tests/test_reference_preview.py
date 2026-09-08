from __future__ import annotations

import asyncio
import json
import socket
import threading

import pytest
import uvicorn

from study_app.app import create_app


@pytest.mark.parametrize("theme", ["light", "dark"])
@pytest.mark.parametrize("phone", [False, True], ids=["hover", "phone-tap"])
def test_packaged_reference_preview_preserves_numbered_and_nested_lists(
    settings_factory, theme, phone
):
    """Exercise the portaled preview, where missing Markdown styling hid list markers."""
    playwright_api = pytest.importorskip("playwright.async_api")
    settings = settings_factory()
    app = create_app(settings, local_mode=True)
    store = app.state.store
    folder = store.create_folder("Reference previews", "reference-previews", None)
    store.create_entry(
        folder["id"],
        "df",
        "Numbered instructions",
        "numbered-instructions",
        "",
        "3. First numbered item\n"
        "   1. Nested numbered item\n"
        "   2. Second nested item\n"
        "4. Second numbered item\n"
        "   - Nested bullet\n"
        "   - Another bullet\n",
    )
    store.create_entry(
        folder["id"],
        "rk",
        "Read the instructions",
        "read-instructions",
        "",
        "Consult @numbered-instructions for the ordered procedure.",
    )
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
            page = await browser.new_page(
                viewport={"width": 390 if phone else 1440, "height": 844 if phone else 1000},
                is_mobile=phone,
                has_touch=phone,
            )
            errors: list[str] = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            await page.add_init_script(f"localStorage.setItem('study-theme', '{theme}')")
            try:
                await page.goto(
                    f"http://127.0.0.1:{port}/library/reference-previews/rk/read-instructions"
                )
                trigger = page.locator(
                    '.reading-pane [data-study-reference-status="resolved"]'
                )
                await trigger.wait_for()
                if phone:
                    await trigger.tap()
                else:
                    await trigger.hover()
                preview = page.locator(".reference-preview-popover")
                expect = playwright_api.expect
                await expect(preview).to_be_visible()
                await expect(preview).to_have_css("opacity", "1")
                await expect(preview.locator("ol")).to_have_count(2)
                await expect(preview.locator("ul")).to_have_count(1)
                await expect(preview.locator("li")).to_have_count(6)
                await expect(preview.locator("ol").first).to_have_attribute("start", "3")
                await expect(preview).to_contain_text("Another bullet")
                # Measure actual browser styles and layout rather than examining
                # CSS source: native markers need a list-item display, a visible
                # list style, and room inside the preview's clipping boundary.
                metrics = await preview.evaluate(
                    """(popup) => {
                      const content = popup.querySelector('.reference-preview-content');
                      const clip = content.getBoundingClientRect();
                      const box = popup.getBoundingClientRect();
                      return {
                        dark: document.documentElement.classList.contains('dark'),
                        viewport: innerWidth,
                        bodyWidth: document.body.scrollWidth,
                        box: {left: box.left, right: box.right},
                        clip: {left: clip.left, right: clip.right, top: clip.top, bottom: clip.bottom},
                        items: [...popup.querySelectorAll('li')].map((item) => {
                          const style = getComputedStyle(item);
                          const marker = getComputedStyle(item, '::marker');
                          const list = item.parentElement;
                          const rect = item.getBoundingClientRect();
                          const parentItem = list.closest('li');
                          return {
                            ordered: list.tagName === 'OL',
                            display: style.display,
                            listStyle: style.listStyleType,
                            markerColor: marker.color,
                            markerSize: parseFloat(marker.fontSize),
                            padding: parseFloat(getComputedStyle(list).paddingInlineStart),
                            left: rect.left, right: rect.right, top: rect.top, bottom: rect.bottom,
                            parentLeft: parentItem?.getBoundingClientRect().left ?? null,
                          };
                        }),
                      };
                    }"""
                )
                (settings.root / "preview-metrics.json").write_text(json.dumps(metrics, indent=2))
                await page.screenshot(path=str(settings.root / "reference-preview.png"))
                assert metrics["dark"] == (theme == "dark")
                assert metrics["box"]["left"] >= 0
                assert metrics["box"]["right"] <= metrics["viewport"]
                assert metrics["bodyWidth"] <= metrics["viewport"]
                for item in metrics["items"]:
                    assert item["display"] == "list-item", item
                    if item["ordered"]:
                        expected_marker = "lower-alpha" if item["parentLeft"] is not None else "decimal"
                        assert item["listStyle"] == expected_marker, item
                    else:
                        assert item["listStyle"] in {"disc", "circle", "square"}, item
                    assert item["markerColor"] not in {"transparent", "rgba(0, 0, 0, 0)"}
                    assert item["markerSize"] >= 10
                    assert item["padding"] >= 16, "list markers need an unclipped gutter"
                    if item["parentLeft"] is not None:
                        assert item["left"] - item["parentLeft"] >= 16
                    assert item["left"] - item["markerSize"] >= metrics["clip"]["left"]
                    assert item["right"] <= metrics["clip"]["right"] + 1
                    assert item["top"] >= metrics["clip"]["top"] - 1
                    assert item["bottom"] <= metrics["clip"]["bottom"] + 1
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
