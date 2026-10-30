from __future__ import annotations

import asyncio
import json
import socket
import threading

import pytest
import uvicorn

from study_app.app import create_app


def test_packaged_proof_review_control_desktop_and_phone(settings_factory, tmp_path):
    playwright_api = pytest.importorskip("playwright.async_api")
    app = create_app(settings_factory(), local_mode=True)
    store = app.state.store
    folder = store.create_folder("Algebra", "algebra", None)
    entry = store.create_entry(
        folder["id"], "th", "Result", "result", "", "A central subgroup is normal."
    )
    entry = store.add_supplement(entry["id"], {
        "kind": "pf", "label": "Proof", "content": "Conjugation preserves the subgroup.",
    })
    original_content = (entry["formulations"], entry["supplements"])
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    origin = f"http://127.0.0.1:{port}"
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

            async def assert_queue(modes):
                await expect(page.get_by_role(
                    "button", name=f"Start review, {len(modes)} due"
                )).to_be_enabled()
                response = await page.request.get(f"{origin}/api/review/queue")
                assert response.ok
                assert [card["mode"] for card in (await response.json())["cards"]] == modes

            try:
                await page.goto(f"{origin}/library/algebra/th/result")
                master = page.get_by_role("checkbox", name="Include this item in review")
                proof = page.get_by_role("checkbox", name="Include proof in review")
                proof_body = page.get_by_text("Conjugation preserves the subgroup.", exact=True)
                await expect(master).to_be_checked()
                await expect(proof).to_be_checked()
                await expect(proof_body).to_be_visible()
                await assert_queue(["statement", "proof-plan"])

                await proof.click()
                await expect(proof).not_to_be_checked()
                await expect(proof).to_be_enabled()
                await expect(master).to_be_checked()
                await expect(page.get_by_text("Statement only", exact=True)).to_be_visible()
                await expect(proof_body).to_be_visible()
                await assert_queue(["statement"])
                saved = store.get_entry(entry["id"])
                assert saved["review_enabled"] is True
                assert saved["proof_review_enabled"] is False
                assert saved["review_modes"] == ["statement", "proof-plan"]
                assert (saved["formulations"], saved["supplements"]) == original_content

                await page.reload()
                await expect(proof).not_to_be_checked()
                await expect(master).to_be_checked()
                await assert_queue(["statement"])

                # The item switch remains the master; neither switch resets the other.
                await master.click()
                await expect(master).not_to_be_checked()
                await expect(proof).not_to_be_checked()
                await expect(proof).to_be_enabled()
                await assert_queue([])
                await proof.click()
                await expect(proof).to_be_checked()
                await expect(proof).to_be_enabled()
                await expect(master).not_to_be_checked()
                await assert_queue([])
                await page.reload()
                await expect(master).not_to_be_checked()
                await expect(proof).to_be_checked()
                await master.click()
                await assert_queue(["statement", "proof-plan"])

                # Hold the failed request so the optimistic state is observable.
                requested = asyncio.Event()
                release_failure = asyncio.Event()

                async def fail_save(route):
                    assert route.request.method == "PATCH"
                    assert route.request.post_data_json == {"proof_review_enabled": False}
                    requested.set()
                    await release_failure.wait()
                    await route.fulfill(
                        status=503, content_type="application/json",
                        body=json.dumps({"detail": "Simulated proof preference failure"}),
                    )

                route_pattern = "**/api/entries/*?include_review_stats=true"
                await page.route(route_pattern, fail_save)
                try:
                    await proof.click()
                    await asyncio.wait_for(requested.wait(), timeout=10)
                    await expect(proof).not_to_be_checked()
                    await expect(proof).to_be_disabled()
                    await expect(master).to_be_checked()
                    assert store.get_entry(entry["id"])["proof_review_enabled"] is True
                finally:
                    release_failure.set()
                await expect(page.locator(".toast-error")).to_contain_text(
                    "Simulated proof preference failure"
                )
                await expect(proof).to_be_checked()
                await expect(proof).to_be_enabled()
                await assert_queue(["statement", "proof-plan"])
                await page.unroute(route_pattern, fail_save)
                await page.locator(".toast-error").click()
                await page.screenshot(path=str(tmp_path / "desktop-proof-review.png"))

                await page.get_by_role("button", name="Toggle dark mode").click()
                await page.set_viewport_size({"width": 390, "height": 844})
                await expect(master).to_be_visible()
                await expect(proof).to_be_visible()
                await expect(page.get_by_role("button", name="Edit", exact=True)).to_be_hidden()
                await proof.focus()
                await page.keyboard.press("Space")
                await expect(proof).not_to_be_checked()
                await expect(proof).to_be_enabled()
                await expect(master).to_be_checked()
                await expect(proof_body).to_be_visible()
                await assert_queue(["statement"])
                await page.reload()
                await expect(proof).not_to_be_checked()
                await expect(master).to_be_checked()
                await proof.click()
                await expect(proof).to_be_checked()
                await expect(proof).to_be_enabled()
                await assert_queue(["statement", "proof-plan"])
                assert store.get_entry(entry["id"])["proof_review_enabled"] is True
                assert await page.evaluate("document.documentElement.scrollWidth <= innerWidth")
                await page.screenshot(path=str(tmp_path / "phone-proof-review.png"))
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
