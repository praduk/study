from __future__ import annotations

import asyncio
import socket
import threading
from datetime import datetime, timedelta, timezone

import pytest
import uvicorn

from study_app.app import create_app


def test_packaged_editor_preview_waits_for_idle_and_saves_current_draft(settings_factory):
    playwright_api = pytest.importorskip('playwright.async_api')
    settings = settings_factory()
    app = create_app(settings, local_mode=True)
    store = app.state.store
    folder = store.create_folder('Preview checks', 'preview-checks', None)
    entry = store.create_entry(
        folder['id'], 'th', 'Preview fixture', 'fixture', 'Original header $x$',
        'Original statement $x^2$.', review_enabled=False,
    )
    entry = store.add_supplement(entry['id'], {
        'kind': 'pf', 'label': 'Proof', 'main': True, 'subtag': None,
        'content': 'Original proof $x^3$.',
    })
    sock = socket.socket()
    sock.bind(('127.0.0.1', 0))
    port = sock.getsockname()[1]
    server = uvicorn.Server(uvicorn.Config(app, log_level='error', ws='none'))
    thread = threading.Thread(target=server.run, kwargs={'sockets': [sock]}, daemon=True)

    async def exercise():
        for _ in range(500):
            if server.started:
                break
            await asyncio.sleep(.01)
        assert server.started
        async with playwright_api.async_playwright() as playwright:
            try:
                browser = await playwright.chromium.launch()
            except playwright_api.Error as exc:
                if "Executable doesn't exist" in str(exc):
                    pytest.skip('Playwright Chromium is not installed')
                raise
            page = await browser.new_page(viewport={'width': 1440, 'height': 1000})
            errors = []
            page.on('pageerror', lambda error: errors.append(str(error)))
            try:
                await page.goto(f'http://127.0.0.1:{port}/library/preview-checks/th/fixture')
                await page.get_by_role('button', name='Edit', exact=True).click()
                preview = page.locator('.editor-preview')
                await preview.locator('mjx-container svg').last.wait_for()
                await page.get_by_role('textbox', name='Custom Markdown header').wait_for()
                now = datetime.now(timezone.utc)
                await page.clock.install(time=now)
                await page.clock.pause_at(now + timedelta(seconds=1))
                await page.evaluate('''() => {
                  window.previewTypesets = 0;
                  const original = MathJax.typesetPromise.bind(MathJax);
                  MathJax.typesetPromise = (elements) => {
                    if (elements.some(e => e.closest('.editor-preview'))) window.previewTypesets++;
                    return original(elements);
                  };
                  window.previewSvg = document.querySelector('.editor-preview mjx-container svg');
                }''')
                editor = page.locator('.editor-dialog .cm-content')
                await editor.click()
                await editor.press('Escape')
                await editor.press('i')
                await editor.press('ControlOrMeta+End')
                await page.keyboard.type(' changed')
                await page.clock.run_for(16)
                await playwright_api.expect(editor).to_contain_text('changed')
                await page.clock.run_for(400)
                assert 'changed' not in await preview.inner_text()
                # Editing the header resets the same idle deadline as body editing.
                await page.get_by_role('textbox', name='Custom Markdown header').fill('Changed header $y$')
                await page.clock.run_for(16)
                await page.clock.run_for(400)
                assert 'Changed header' not in await preview.inner_text()
                assert 'changed' not in await preview.inner_text()
                assert await page.evaluate('window.previewTypesets') == 0
                assert await page.evaluate('window.previewSvg.isConnected')
                await page.clock.run_for(101)
                await playwright_api.expect(preview).to_contain_text('Changed header')
                await playwright_api.expect(preview).to_contain_text('changed')
                await playwright_api.expect(preview).to_have_attribute('aria-busy', 'false')
                await playwright_api.expect(preview.locator('mjx-container svg')).to_have_count(2)
                assert await page.evaluate('window.previewTypesets') == 2

                # Changing variants must show the selected variant immediately.
                await page.get_by_role('button', name='pf: Proof · main', exact=True).click()
                await playwright_api.expect(preview).to_contain_text('Original proof')
                await editor.click()
                await editor.press('Escape')
                await editor.press('i')
                await editor.press('ControlOrMeta+End')
                await page.keyboard.type(' latest proof')
                await page.clock.run_for(16)
                await page.get_by_role('button', name='Main · main', exact=True).click()
                await playwright_api.expect(preview).to_contain_text('Original statement')
                assert 'latest proof' not in await preview.inner_text()
                await page.clock.run_for(600)
                assert 'latest proof' not in await preview.inner_text()
                await page.get_by_role('button', name='pf: Proof · main', exact=True).click()
                await playwright_api.expect(preview).to_contain_text('latest proof')

                # Disabling preview cancels work; enabling it shows the current draft.
                await editor.click()
                await editor.press('Escape')
                await editor.press('i')
                await editor.press('ControlOrMeta+End')
                await page.keyboard.type(' hidden edit')
                await page.clock.run_for(16)
                await page.get_by_role('button', name='Preview', exact=True).click()
                calls = await page.evaluate('window.previewTypesets')
                await page.clock.run_for(600)
                assert await page.evaluate('window.previewTypesets') == calls
                await page.get_by_role('button', name='Preview', exact=True).click()
                await playwright_api.expect(preview).to_contain_text('hidden edit')

                # Save before the idle timer expires: persisted content must be current.
                await editor.click()
                await editor.press('Escape')
                await editor.press('i')
                await editor.press('ControlOrMeta+End')
                await page.keyboard.type(' save immediately')
                await page.clock.run_for(16)
                assert 'save immediately' not in await preview.inner_text()
                async with page.expect_response(lambda response: (
                    response.request.method == 'PUT'
                    and response.url.endswith(f"/content/{entry['supplements'][0]['id']}")
                )):
                    await page.get_by_role('button', name='Save', exact=True).click()
                saved = store.get_entry(entry['id'])
                assert 'changed' in saved['formulations'][0]['content']
                assert 'save immediately' in saved['supplements'][0]['content']
                assert saved['header'] == 'Changed header $y$'
                assert not errors
            finally:
                await browser.close()

    try:
        thread.start()
        asyncio.run(exercise())
    finally:
        server.should_exit = True
        thread.join(timeout=10)
        sock.close()
