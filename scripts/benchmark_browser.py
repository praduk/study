"""Measure Study browser actions using only a disposable copy of its data.

Use --source-root to compare a frozen checkout and the current built checkout.
Cold means a fresh browser context; the server stays running between samples.
Reported timings include Playwright actionability checks, API work and UI render.
Readiness polls the DOM every 10 ms; slow assertion retry intervals are excluded.
No latency thresholds are asserted. Only synthetic entries receive review grades.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import shutil
import socket
import statistics
import sys
import tempfile
import threading
import time
from collections import Counter
from pathlib import Path
from unittest.mock import patch
from urllib.parse import urlsplit


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--git-root", type=Path, help="Read-only Git status root; defaults to source root")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--samples", type=int, default=3)
    parser.add_argument("--focus", choices=("everyday", "deletion"), default="everyday",
                        help="Run all everyday actions or a focused synthetic deletion benchmark")
    args = parser.parse_args()
    if args.samples < 1:
        parser.error("--samples must be positive")
    source = args.source_root.resolve()
    git_root = (args.git_root or source).resolve()
    sys.path.insert(0, str(source))
    import uvicorn
    from playwright.async_api import async_playwright, expect
    from starlette.responses import JSONResponse

    import study_app.app as app_module
    from study_app.config import Settings
    from study_app.git_ops import GitRepository

    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    evidence = output.parent / f"{output.stem}-screenshots"
    evidence.mkdir(exist_ok=True)
    results = {
        "method": "Chromium; fresh context per sample; persistent prewarmed local server; disposable data copy",
        "source_root": str(source), "git_root": str(git_root), "samples_per_viewport": args.samples,
        "readiness_poll_ms": 10, "search_key_delay_ms": 20, "focus": args.focus,
        "actions": {}, "browser_errors": [], "api_errors": [], "screenshots": [],
    }

    def save():
        output.write_text(json.dumps(results, indent=2) + "\n")

    def record(name, elapsed, requests):
        row = results["actions"].setdefault(name, {"samples_ms": [], "api_requests": []})
        row["samples_ms"].append(round(elapsed, 2))
        counts = Counter(f"{method} {path}" for method, path in requests)
        row["api_requests"].append(dict(sorted(counts.items())))
        values = row["samples_ms"]
        row.update(n=len(values), median_ms=round(statistics.median(values), 2),
                   min_ms=min(values), max_ms=max(values))
        print(name, round(elapsed, 2), flush=True)
        save()

    with tempfile.TemporaryDirectory(prefix="study-browser-benchmark-") as temporary:
        root = Path(temporary)
        shutil.copytree(source / "data", root / "data",
                        ignore=shutil.ignore_patterns("runtime", "exports"))
        settings = Settings(root, 8765, "127.0.0.1", ("127.0.0.1",), "", 30, False, 12, 32)
        with patch.object(app_module, "GitRepository", lambda *unused: GitRepository(git_root, git_root / "data")):
            app = app_module.create_app(settings, local_mode=True)

        @app.middleware("http")
        async def block_source_git_writes(request, call_next):
            if request.url.path.startswith("/api/git/") and request.method != "GET":
                return JSONResponse({"detail": "Git writes are disabled in this benchmark"}, status_code=403)
            return await call_next(request)

        store = app.state.store
        snapshot = store.snapshot()
        results["library"] = {"entries": len(snapshot["entries"]), "folders": len(snapshot["folders"])}
        # Select a real theorem with a proof, mathematics, and actual references.
        candidates = sorted((item for item in snapshot["entries"] if item["kind"] == "th" and item["supplements"]),
                            key=lambda item: item["canonical_tag"])
        target = None
        for candidate in candidates:
            detail = store.get_entry(candidate["id"])
            content = "\n".join(item.get("content", "") for item in detail["formulations"] + detail["supplements"])
            if "@" in content and "$" in content:
                target = detail
                break
        if target is None:
            raise RuntimeError("The benchmark requires a theorem with math, a proof, and references")
        results["target"] = {"entry_id": target["id"], "canonical_tag": target["canonical_tag"]}
        path = "/library/" + target["canonical_tag"].replace(":", "/")
        target_folder = next(item for item in snapshot["folders"] if item["id"] == target["folder_id"])
        fixture_folder = store.create_folder("Browser performance fixture", "browser-performance-fixture", None, index=0)
        sock = socket.socket()
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
        base = f"http://127.0.0.1:{port}"
        server = uvicorn.Server(uvicorn.Config(app, log_level="error", ws="none"))
        thread = threading.Thread(target=server.run, kwargs={"sockets": [sock]}, daemon=True)

        async def run():
            for _ in range(1000):
                if server.started:
                    break
                await asyncio.sleep(.01)
            assert server.started, "temporary Study server did not start"
            async with async_playwright() as playwright:
                browser = await playwright.chromium.launch()
                try:
                    async def exercise_sample(phone, sample):
                        label = "phone" if phone else "desktop"
                        fixture = store.create_entry(
                            fixture_folder["id"], "df", f"Synthetic browser fixture {label} {sample + 1}",
                            f"synthetic-{label}-{sample + 1}", "", "The synthetic value is $1$.", index=0,
                            review_enabled=args.focus != "deletion")
                        if args.focus == "deletion":
                            successor = store.create_entry(
                                fixture_folder["id"], "df", f"Synthetic successor {sample + 1}",
                                f"successor-{sample + 1}", "", "The successor value is $2$.", index=1,
                                review_enabled=False)
                            empty_folder = store.create_folder(
                                f"Synthetic empty folder {sample + 1}", f"empty-{sample + 1}", fixture_folder["id"])
                            subtree = store.create_folder(
                                f"Synthetic subtree {sample + 1}", f"subtree-{sample + 1}", fixture_folder["id"])
                            child = store.create_folder("Synthetic child", "child", subtree["id"])
                            subtree_entries = [store.create_entry(
                                owner, "df", f"Synthetic subtree entry {number + 1}", f"entry-{number + 1}",
                                "", "A disposable statement.", review_enabled=False)
                                for number, owner in enumerate((subtree["id"], child["id"], child["id"]))]
                        # Fixture authoring is setup, not part of browser startup.
                        # Match create_app's prewarmed library and search snapshot.
                        store.snapshot()
                        store.reload_search_index()
                        context = await browser.new_context(
                            viewport={"width": 390 if phone else 1440, "height": 844 if phone else 1000},
                            is_mobile=phone, has_touch=phone, color_scheme="light")
                        page = await context.new_page()
                        page.set_default_timeout(30000)
                        requests = []
                        page.on("request", lambda request: requests.append((request.method, urlsplit(request.url).path))
                                if "/api/" in request.url else None)
                        page.on("pageerror", lambda error: results["browser_errors"].append({
                            "viewport": label, "sample": sample + 1, "error": str(error)}))
                        page.on("response", lambda response: results["api_errors"].append({
                            "viewport": label, "sample": sample + 1,
                            "method": response.request.method, "path": urlsplit(response.url).path,
                            "status": response.status}) if "/api/" in response.url and response.status >= 400 else None)
                        await page.add_init_script("""(() => {
                          localStorage.setItem('study-theme', 'light');
                          const original = window.fetch;
                          window.__benchmarkPending = 0;
                          window.fetch = async (...args) => {
                            window.__benchmarkPending++;
                            try { return await original(...args); }
                            finally { window.__benchmarkPending--; }
                          };
                        })()""")

                        async def condition(expression, arg=None):
                            # Poll through CDP; wait_for_function uses eval in page context,
                            # which correctly becomes unavailable under Study's strict CSP.
                            deadline = time.perf_counter() + 30
                            while not await page.evaluate(expression, arg):
                                if time.perf_counter() >= deadline:
                                    raise AssertionError("Browser readiness condition timed out")
                                await asyncio.sleep(.01)

                        async def api_idle():
                            await condition("() => window.__benchmarkPending === 0")

                        async def math_ready(scope=".reading-pane"):
                            await condition("""scope => {
                              const root = document.querySelector(scope);
                              if (!root) return false;
                              return [...root.querySelectorAll('.math-inline-source, .math-display-source')]
                                .every(node => node.querySelector('mjx-container'));
                            }""", arg=scope)

                        async def visible(selector):
                            await condition("""selector => {
                              const element = document.querySelector(selector);
                              return element && element.getClientRects().length > 0
                                && getComputedStyle(element).visibility !== 'hidden';
                            }""", selector)

                        async def missing(selector):
                            await condition("selector => !document.querySelector(selector)", selector)

                        async def text_ready(selector, text, *, different=False, contains=False):
                            await condition("""({selector, text, different, contains}) => {
                              const value = document.querySelector(selector)?.textContent;
                              if (value === undefined) return false;
                              const matches = contains ? value.includes(text) : value === text;
                              return different ? !matches : matches;
                            }""", {"selector": selector, "text": text, "different": different, "contains": contains})

                        async def locator_ready(locator, expression, arg=None):
                            deadline = time.perf_counter() + 30
                            while not await locator.evaluate(expression, arg):
                                if time.perf_counter() >= deadline:
                                    raise AssertionError("Locator readiness condition timed out")
                                await asyncio.sleep(.01)

                        async def checkbox_ready(locator, checked):
                            await locator_ready(locator, """(element, checked) => {
                              const value = element.getAttribute('aria-checked');
                              const actual = value === null ? element.checked : value === 'true';
                              return actual === checked && !element.disabled
                                && element.getAttribute('aria-disabled') !== 'true';
                            }""", checked)

                        async def settled():
                            await visible(".document-heading h1")
                            await visible('.linked-items[aria-busy="false"]')
                            await missing('.reading-pane [data-study-reference-status="loading"]')
                            await math_ready()
                            await api_idle()

                        async def measure(name, action):
                            start_count = len(requests)
                            start = time.perf_counter()
                            await action()
                            elapsed = (time.perf_counter() - start) * 1000
                            # Assertions happen after the timing endpoint so their retry
                            # schedule cannot quantize the measured UI latency.
                            await expect(page.locator(".toast-error:visible, .form-error:visible")).to_have_count(0)
                            await api_idle()
                            record(f"{label}.{name}", elapsed, requests[start_count:])

                        async def screenshot(name):
                            filename = evidence / f"{label}-{sample + 1}-{name}.png"
                            # Evidence should show the finished layout, not a fade's
                            # intermediate opacity. This runs outside measured actions.
                            await page.screenshot(path=str(filename), animations="disabled")
                            results["screenshots"].append(str(filename))
                            save()

                        try:
                            if args.focus == "deletion":
                                results["deletion_method"] = "Desktop confirmation submit to dialog close, correct surviving selection, math/backlinks settled; only synthetic records are deleted."
                                await page.goto(base + "/library/" + fixture["canonical_tag"].replace(":", "/"), wait_until="domcontentloaded")
                                await text_ready(".document-heading h1", fixture["title"])
                                await settled()
                                await page.locator(".document-actions").get_by_role("button", name="Delete", exact=True).click()
                                dialog = page.locator(".delete-item-dialog")
                                await expect(dialog).to_contain_text(fixture["title"])

                                async def delete_entry():
                                    await dialog.get_by_role("button", name="Delete entry", exact=True).click()
                                    await missing(".delete-item-dialog")
                                    await text_ready(".document-heading h1", successor["title"])
                                    await settled()
                                await measure("delete_entry", delete_entry)
                                await expect(page.locator(".entry-row").filter(has_text=fixture["title"])).to_have_count(0)
                                assert fixture["id"] not in {item["id"] for item in store.snapshot()["entries"]}
                                await screenshot("deleted-entry")

                                async def prepare_folder(folder, recursive):
                                    await page.get_by_role("button", name=folder["name"], exact=True).click()
                                    await page.locator(".sidebar-create").get_by_role("button", name="Delete", exact=True).click()
                                    await expect(dialog).to_contain_text(folder["name"])
                                    if recursive:
                                        await expect(dialog.get_by_role("button", name="Delete recursively", exact=True)).to_be_disabled()
                                        await page.locator("#delete-folder-confirmation").fill(folder["name"])
                                    else:
                                        await expect(page.locator("#delete-folder-confirmation")).to_have_count(0)

                                await prepare_folder(empty_folder, False)

                                async def delete_empty():
                                    await dialog.get_by_role("button", name="Delete folder", exact=True).click()
                                    await missing(".delete-item-dialog")
                                    await condition("name => ![...document.querySelectorAll('.folder-name')].some(button => button.textContent === name)", empty_folder["name"])
                                    await text_ready(".document-heading h1", successor["title"])
                                    await settled()
                                await measure("delete_empty_folder", delete_empty)
                                assert empty_folder["id"] not in {item["id"] for item in store.snapshot()["folders"]}
                                await screenshot("deleted-empty-folder")

                                await prepare_folder(subtree, True)

                                async def delete_subtree():
                                    await dialog.get_by_role("button", name="Delete recursively", exact=True).click()
                                    await missing(".delete-item-dialog")
                                    await condition("name => ![...document.querySelectorAll('.folder-name')].some(button => button.textContent === name)", subtree["name"])
                                    await text_ready(".document-heading h1", successor["title"])
                                    await settled()
                                await measure("delete_folder_subtree", delete_subtree)
                                remaining = store.snapshot()
                                assert {subtree["id"], child["id"]}.isdisjoint({item["id"] for item in remaining["folders"]})
                                assert {entry["id"] for entry in subtree_entries}.isdisjoint({item["id"] for item in remaining["entries"]})
                                await screenshot("deleted-subtree")
                                assert not results["browser_errors"], results["browser_errors"]
                                return

                            start = time.perf_counter()
                            await page.goto(base + path, wait_until="domcontentloaded")
                            await text_ready(".document-heading h1", target["title"])
                            record(f"{label}.cold_content_ready", (time.perf_counter() - start) * 1000, requests)
                            await settled()
                            record(f"{label}.cold_settled", (time.perf_counter() - start) * 1000, requests)
                            assert await page.locator('.reading-pane mjx-container').count() > 0
                            await screenshot("reader-light")

                            async def reload():
                                await page.reload(wait_until="domcontentloaded")
                                await settled()
                            await measure("warm_reload_settled", reload)

                            active_index = await page.locator(".entry-row").evaluate_all(
                                "rows => rows.findIndex(row => row.classList.contains('active'))")

                            async def navigate_next():
                                previous = await page.locator(".document-heading h1").inner_text()
                                if phone:
                                    await page.locator(".reading-sequence-nav button").last.click()
                                else:
                                    await page.locator(".entry-row").nth(active_index + 1).click()
                                await text_ready(".document-heading h1", previous, different=True)
                                await settled()
                            await measure("next_entry", navigate_next)

                            async def navigate_previous():
                                if phone:
                                    await page.locator(".reading-sequence-nav button").first.click()
                                else:
                                    await page.locator(".entry-row").nth(active_index).click()
                                await text_ready(".document-heading h1", target["title"])
                                await settled()
                            await measure("previous_entry", navigate_previous)

                            async def search():
                                await page.get_by_role("searchbox", name="Search your library").fill("group")
                                await text_ready(".search-status", "result", contains=True)
                                assert await page.locator(".search-results button").count() > 0
                            await measure("search_results", search)
                            await page.get_by_role("searchbox", name="Search your library").press("Escape")

                            async def type_search():
                                await page.get_by_role("searchbox", name="Search your library").press_sequentially("group", delay=20)
                                await text_ready(".search-status", "result", contains=True)
                                assert await page.locator(".search-results button").count() > 0
                            await measure("search_typing_results", type_search)
                            await page.get_by_role("searchbox", name="Search your library").press("Escape")

                            async def reference():
                                trigger = page.locator('.reading-pane [data-study-reference-status="resolved"]').first
                                await trigger.scroll_into_view_if_needed()
                                if phone:
                                    await trigger.tap()
                                else:
                                    await trigger.hover()
                                await visible(".reference-preview-popover")
                                await math_ready(".reference-preview-popover")
                            await measure("reference_preview", reference)
                            await screenshot("reference")
                            await page.keyboard.press("Escape")
                            await page.mouse.move(0, 0)

                            async def theme():
                                if phone:
                                    await page.get_by_role("button", name="Open Study library").click()
                                    await page.get_by_role("button", name="Dark mode", exact=True).click()
                                    await page.get_by_role("button", name="Close library", exact=True).click()
                                else:
                                    await page.get_by_role("button", name="Toggle dark mode").click()
                                await condition("() => document.documentElement.classList.contains('dark')")
                                await settled()
                            await measure("dark_theme", theme)
                            await screenshot("reader-dark")
                            assert await page.evaluate("document.documentElement.scrollWidth <= innerWidth")

                            control = page.get_by_role("checkbox", name="Include this item in review")
                            original_checked = await control.is_checked()

                            async def toggle_entry():
                                await control.click()
                                await checkbox_ready(control, not original_checked)
                            await measure("entry_review_toggle", toggle_entry)
                            await control.click()
                            await expect(control).to_be_checked(checked=original_checked)
                            await expect(control).to_be_enabled()
                            await api_idle()

                            if not phone:
                                folder_control = page.get_by_role("checkbox", name=f"Include {target_folder['name']} in review", exact=True)
                                original_folder_checked = await folder_control.is_checked()

                                async def toggle_folder():
                                    await folder_control.click()
                                    await checkbox_ready(folder_control, not original_folder_checked)
                                await measure("folder_review_toggle", toggle_folder)
                                await folder_control.click()
                                await expect(folder_control).to_be_checked(checked=original_folder_checked)
                                await expect(folder_control).to_be_enabled()
                                await api_idle()

                                async def resize():
                                    handle = page.get_by_role("button", name="Resize library panel", exact=False)
                                    await handle.focus()
                                    await page.keyboard.press("End")
                                    await locator_ready(handle, "element => element.getAttribute('aria-label') === 'Resize library panel; current width 520 pixels'")
                                await measure("library_resize", resize)
                                await page.get_by_role("button", name="Resize library panel", exact=False).press("Home")

                                async def hide_library():
                                    await page.get_by_role("button", name="Hide library panel").click()
                                    await condition("() => document.querySelector('.app-frame')?.classList.contains('library-closed')")
                                await measure("library_hide", hide_library)
                                await page.get_by_role("button", name="Show library panel").click()
                                chevron = page.locator(".tree > .folder-row-group .tree-chevron").first
                                was_open = await chevron.get_attribute("aria-label") == "Collapse folder"

                                async def expand_collapse():
                                    await chevron.click()
                                    await locator_ready(chevron, "(element, label) => element.getAttribute('aria-label') === label", "Expand folder" if was_open else "Collapse folder")
                                await measure("library_expand_collapse", expand_collapse)
                                await chevron.click()
                            else:
                                async def drawer():
                                    await page.get_by_role("button", name="Open Study library").click()
                                    await visible("#study-library-sidebar.mobile-open")
                                    await locator_ready(page.get_by_role("button", name="Close library", exact=True), "element => document.activeElement === element")
                                await measure("library_drawer", drawer)
                                await page.keyboard.press("Shift+Tab")
                                assert await page.evaluate("document.getElementById('study-library-sidebar').contains(document.activeElement)")
                                await page.keyboard.press("Escape")
                                await expect(page.get_by_role("button", name="Open Study library")).to_be_focused()

                            async def open_calendar():
                                if phone:
                                    await page.get_by_role("button", name="Open Study library").click()
                                    await page.locator(".mobile-sidebar-actions").get_by_role("button", name="Calendar").click()
                                else:
                                    await page.get_by_role("button", name="Calendar", exact=True).click()
                                await condition("() => document.querySelector('.calendar-board')?.getAttribute('aria-busy') === 'false'")
                                await visible(".calendar-agenda" if phone else ".calendar-board")
                            await measure("calendar_open", open_calendar)

                            async def next_month():
                                prior = await page.locator(".calendar-top h1").inner_text()
                                await page.get_by_role("button", name="Next month").click()
                                await text_ready(".calendar-top h1", prior, different=True)
                                await condition("() => document.querySelector('.calendar-board')?.getAttribute('aria-busy') === 'false'")
                                await visible(".calendar-agenda" if phone else ".calendar-board")
                            await measure("calendar_next_month", next_month)
                            await screenshot("calendar")
                            await page.get_by_role("button", name="Library", exact=True).click()
                            await settled()

                            async def review_open():
                                if phone:
                                    await page.get_by_role("button", name="Open Study library").click()
                                    await page.locator(".mobile-sidebar-actions").get_by_role("button", name="Review", exact=False).click()
                                else:
                                    await page.get_by_role("button", name="Start review", exact=False).click()
                                await text_ready(".review-stage h1", fixture["title"])
                            await measure("review_open", review_open)
                            assert await page.locator(".review-stage h1").inner_text() == fixture["title"]
                            await page.get_by_role("button", name="Somewhat", exact=True).click()

                            async def reveal():
                                await page.get_by_role("button", name="Reveal and compare", exact=True).click()
                                await visible(".feedback-panel")
                                await math_ready(".feedback-panel")
                            await measure("review_reveal_synthetic", reveal)
                            await screenshot("review")

                            async def grade():
                                # The preceding title assertion guards every benchmark grade.
                                await page.locator(".grade-good").click()
                                await condition("""() =>
                                  document.querySelector('.review-count')?.textContent.startsWith('1 completed')
                                  || document.querySelector('.review-empty.complete h1')?.textContent === 'Review complete'
                                """)
                                await missing(".feedback-panel")
                            await measure("review_grade_synthetic", grade)
                            await page.get_by_role("button", name="Library", exact=True).click()
                            await settled()

                            if not phone:
                                async def editor_open():
                                    await page.get_by_role("button", name="Edit", exact=True).click()
                                    await visible(".editor-dialog .cm-content")
                                await measure("editor_open", editor_open)
                                saved_title = target["title"] + " (benchmark copy)"
                                await page.get_by_label("Title", exact=True).fill(saved_title)

                                async def save_title():
                                    await page.locator(".editor-dialog").get_by_role("button", name="Save", exact=True).click()
                                    await missing(".editor-dialog")
                                    await text_ready(".document-heading h1", saved_title)
                                    await settled()
                                await measure("editor_title_save", save_title)
                                await page.get_by_role("button", name="Edit", exact=True).click()
                                await expect(page.get_by_label("Title", exact=True)).to_have_value(saved_title)
                                await page.get_by_label("Title", exact=True).fill(target["title"])
                                await page.locator(".editor-dialog").get_by_role("button", name="Save", exact=True).click()
                                await missing(".editor-dialog")
                                await settled()

                                await measure("editor_reopen", editor_open)
                                original_body = next(item for item in target["formulations"] if item["main"])["content"]
                                await page.locator(".editor-dialog .cm-content").fill(original_body + "\n\nDisposable benchmark note.")

                                async def save_body():
                                    await page.locator(".editor-dialog").get_by_role("button", name="Save", exact=True).click()
                                    await missing(".editor-dialog")
                                    await text_ready(".reading-pane", "Disposable benchmark note.", contains=True)
                                    await settled()
                                await measure("editor_body_save", save_body)
                                await editor_open()
                                await page.locator(".editor-dialog .cm-content").fill(original_body)
                                await page.locator(".editor-dialog").get_by_role("button", name="Save", exact=True).click()
                                await missing(".editor-dialog")
                                await text_ready(".reading-pane", "Disposable benchmark note.", contains=True, different=True)
                                await settled()
                                await editor_open()

                                async def unchanged_save():
                                    await page.locator(".editor-dialog").get_by_role("button", name="Save", exact=True).click()
                                    await missing(".editor-dialog")
                                await measure("editor_unchanged_save", unchanged_save)

                                async def dialogs():
                                    controls = [
                                        (page.get_by_role("button", name="Move", exact=True), ".move-folder-dialog", "Cancel"),
                                        (page.get_by_role("button", name="Edit global LaTeX macros"), ".macros-dialog", "Cancel"),
                                        (page.locator(".top-actions button").filter(has=page.locator("svg.lucide-git-branch")), ".git-dialog", "Done"),
                                    ]
                                    export_button = page.get_by_role("button", name="Export PDF", exact=True)
                                    if await export_button.count():
                                        controls.append((export_button, ".export-dialog", "Cancel"))
                                    for button, popup, close_label in controls:
                                        for _ in range(2):
                                            await button.click()
                                            await visible(popup)
                                            await page.locator(popup).get_by_role("button", name=close_label, exact=True).click()
                                            await missing(popup)
                                await measure("dialogs_reopen", dialogs)
                            assert not results["browser_errors"], results["browser_errors"]
                        except Exception as error:
                            results["failure"] = {"viewport": label, "sample": sample + 1, "error": repr(error)}
                            await screenshot("failure")
                            save()
                            raise
                        finally:
                            await context.close()

                    for phone in ((False,) if args.focus == "deletion" else (False, True)):
                        for sample in range(args.samples):
                            await exercise_sample(phone, sample)
                finally:
                    await browser.close()

        thread.start()
        try:
            asyncio.run(run())
        finally:
            server.should_exit = True
            thread.join(timeout=5)
            sock.close()
            save()


if __name__ == "__main__":
    main()
