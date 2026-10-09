from __future__ import annotations

import asyncio
import re
import socket
import threading

import pytest
import uvicorn
from fastapi.testclient import TestClient

from study_app.app import create_app
from study_app.export import build_export_html

SOURCE = r'''\begin{tikzcd}
\R \arrow[r, "f"] & B
\end{tikzcd}'''


def test_only_quiver_editor_can_be_framed(settings_factory):
    app = create_app(settings_factory(), local_mode=True)
    with TestClient(app, base_url='http://127.0.0.1', client=('127.0.0.1', 50000)) as client:
        for path in ['/', '/library/anything', '/vendor/quiver/index.html']:
            response = client.get(path)
            assert response.status_code == 200
            is_editor = path == '/vendor/quiver/index.html'
            assert response.headers['x-frame-options'] == ('SAMEORIGIN' if is_editor else 'DENY')
            ancestor = "'self'" if is_editor else "'none'"
            assert f'frame-ancestors {ancestor}' in response.headers['content-security-policy']


def test_export_tikz_source_is_escaped_and_runtime_is_conditional(settings_factory):
    store = create_app(settings_factory(), local_mode=True).state.store
    folder = store.create_folder('Diagrams', 'diagrams', None)
    entry = store.create_entry(folder['id'], 'df', 'Fixture', 'fixture', '', 'Ordinary $x$.')
    ordinary = build_export_html(store, [entry], 'Fixture', True)
    assert '/vendor/tikzjax/' not in ordinary
    assert '[tex]/mhchem' in ordinary
    entry = store.write_variant_content(entry['id'], entry['formulations'][0]['id'],
                                 '```tikzcd\n' + SOURCE + '\n% <script>unsafe</script>\n```')
    rendered = build_export_html(store, [entry], 'Fixture', True)
    assert 'data-tikzcd-source=' in rendered
    assert '% &lt;script&gt;unsafe&lt;/script&gt;' in rendered
    assert '<script>unsafe</script>' not in rendered
    assert '/vendor/tikzjax/study-export.mjs' in rendered


def test_packaged_tikz_button_create_edit_code_canvas_and_font_size(settings_factory):
    playwright_api = pytest.importorskip('playwright.async_api')
    settings = settings_factory()
    app = create_app(settings, local_mode=True)
    store = app.state.store
    folder = store.create_folder('Diagram checks', 'diagram-checks', None)
    store.set_macros({'R': r'\mathbb{R}', 'Hom': r'\operatorname{Hom}'})
    entry = store.create_entry(folder['id'], 'th', 'Diagram fixture', 'fixture', '',
                               'Before $B$.\n\n```tikzcd\n' + SOURCE + '\n```\n\nAfter.', review_enabled=False)
    store.add_supplement(entry['id'], {'kind': 'pf', 'label': 'Main', 'main': True,
                                     'subtag': None, 'content': 'Proof $B$.\n\n```tikzcd\n' + SOURCE + '\n```'})
    sock = socket.socket()
    sock.bind(('127.0.0.1', 0))
    port = sock.getsockname()[1]
    base = f'http://127.0.0.1:{port}'
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
            page.set_default_timeout(30000)
            errors, remote = [], []
            page.on('pageerror', lambda error: errors.append(error.stack))
            page.on('request', lambda request: remote.append(request.url)
                    if not request.url.startswith((base, 'data:', 'blob:')) else None)
            try:
                await page.goto(base + '/library/diagram-checks/th/fixture')
                await page.locator('.reading-pane .tikzcd-svg svg').last.wait_for()
                await page.evaluate('document.fonts.ready')
                async def sizes(selector):
                    return await page.locator(selector).evaluate('''el => {
                      const svg = el.querySelector('.tikzcd-svg svg');
                      const b = [...svg.querySelectorAll('text')].find(t => t.textContent === '\\uf042');
                      return {font:parseFloat(getComputedStyle(svg).fontSize),
                        bSize:parseFloat(b.getAttribute('font-size')) * Math.abs(b.getScreenCTM().a),
                        mathHeight:el.querySelector('mjx-container svg').getBoundingClientRect().height,
                        width:svg.getAttribute('width')};
                    }''')
                for selector in ['.reading-pane > .markdown-body', '.supplement-list .markdown-body']:
                    metric = await sizes(selector)
                    assert metric['width'].endswith('em')
                    assert abs(metric['bSize'] / metric['font'] - 1) < .02
                    assert .65 < metric['mathHeight'] / metric['bSize'] < .85
                await page.screenshot(path=str(settings.root / 'tikz-reader-light.png'))
                await page.get_by_role('button', name='Edit', exact=True).click()
                editor = page.locator('.editor-dialog .cm-content')
                button = page.get_by_role('button', name='TikZ-CD', exact=True)
                # Cursor movement alone must not open the diagram editor.
                await editor.locator('.cm-line').filter(has_text=r'\begin{tikzcd}').click()
                assert not await page.locator('.tikzcd-dialog').count()
                await button.click()
                await playwright_api.expect(page.get_by_role('button', name='Replace diagram', exact=True)).to_be_visible()
                code = page.get_by_role('textbox', name='TikZ-CD code', exact=True)
                await playwright_api.expect(code).to_have_value(SOURCE)
                await playwright_api.expect(page.get_by_role('button', name='Apply code to canvas', exact=True)).to_be_enabled()
                frame = page.frame_locator('iframe[title="Visual commutative diagram editor"]')
                await playwright_api.expect(frame.locator('#welcome-pane')).not_to_be_visible()
                assert await frame.locator('select[name="renderer"] option').count() == 1
                # A no-op edit preserves source, rather than Quiver's canonical export.
                await page.get_by_role('button', name='Replace diagram', exact=True).click()
                await playwright_api.expect(page.locator('.tikzcd-dialog')).not_to_be_visible(timeout=30000)
                assert SOURCE in await editor.inner_text()
                # The very same button creates when the cursor is outside a block.
                await editor.click()
                await editor.press('Escape')
                await editor.press('g')
                await editor.press('g')
                await button.click()
                await playwright_api.expect(page.get_by_role('button', name='Insert TikZ-CD', exact=True)).to_be_visible()
                await page.locator('.tikzcd-dialog').get_by_role('button', name='Cancel', exact=True).click()
                await editor.locator('.cm-line').filter(has_text=r'\begin{tikzcd}').click()
                await button.click()
                await playwright_api.expect(code).to_have_value(SOURCE)
                await playwright_api.expect(page.get_by_role('button', name='Apply code to canvas', exact=True)).to_be_enabled()
                edited = r'\begin{tikzcd} \R \arrow[r, "{\Hom(A,B)}"] & B \end{tikzcd}'
                await code.fill(edited)
                await page.get_by_role('button', name='Apply code to canvas', exact=True).click()
                await playwright_api.expect(page.get_by_role('button', name='Apply code to canvas', exact=True)).to_be_enabled()
                frame = page.frame_locator('iframe[title="Visual commutative diagram editor"]')
                await frame.locator('.vertex .katex svg').last.wait_for()
                assert not await frame.locator('.katex-error').count()
                await frame.locator('.vertex').last.click()
                await frame.locator('.label-input').fill('Z')
                await playwright_api.expect(code).to_have_value(re.compile('Z'))
                await page.screenshot(path=str(settings.root / 'tikz-editor.png'))
                # Failed compilation is visible; a subsequent correction must recover.
                await code.fill(r'\begin{tikzcd} \notarealmacro \arrow[r] & B \end{tikzcd}')
                await page.get_by_role('button', name='Render preview', exact=True).click()
                await page.locator('.tikzcd-code-preview .form-error').wait_for()
                await page.get_by_role('button', name='Replace diagram', exact=True).click()
                await page.locator('.tikzcd-dialog > .form-error').wait_for()
                assert SOURCE in await editor.inner_text()
                preserved = edited.replace('& B', '& Z').replace(r'\begin{tikzcd}', r'\begin{tikzcd}[nodes={red}]')
                await code.fill(preserved)
                await page.get_by_role('button', name='Apply code to canvas', exact=True).click()
                await playwright_api.expect(page.get_by_role('button', name='Apply code to canvas', exact=True)).to_be_enabled()
                await playwright_api.expect(page.locator('.tikzcd-dialog .safety-note')).to_contain_text('Unknown diagram option')
                await playwright_api.expect(code).to_have_value(preserved)
                await playwright_api.expect(page.locator('.quiver-frame')).to_have_class(re.compile('inactive'))
                await page.get_by_role('button', name='Replace diagram', exact=True).click()
                await playwright_api.expect(page.locator('.tikzcd-dialog')).not_to_be_visible(timeout=30000)
                await page.locator('.editor-preview .tikzcd-svg svg').wait_for()
                metric = await page.locator('.editor-preview .tikzcd-svg svg').evaluate('''svg => {
                  const t=svg.querySelector('text'); return parseFloat(t.getAttribute('font-size')) *
                    Math.abs(t.getScreenCTM().a)/parseFloat(getComputedStyle(svg).fontSize);
                }''')
                assert abs(metric - 1) < .02
                await page.get_by_role('button', name='Save', exact=True).click()
                await playwright_api.expect(page.get_by_role('dialog')).not_to_be_visible()
                saved = store.get_entry(entry['id'])
                content = saved['formulations'][0]['content']
                assert content.count('```tikzcd') == 1
                assert content.startswith('Before $B$.') and content.rstrip().endswith('After.')
                assert r'\Hom(A,B)' in content and '& Z' in content
                assert preserved in content
                assert saved['assets'] == []
                await page.get_by_role('button', name='Toggle dark mode', exact=True).click()
                await page.set_viewport_size({'width': 390, 'height': 844})
                await page.locator('.reading-pane .tikzcd-svg svg').first.wait_for()
                await page.screenshot(path=str(settings.root / 'tikz-phone-dark.png'))
                assert await page.evaluate('document.documentElement.scrollWidth <= innerWidth')
                # Sanitise worker output and keep repeated SVG IDs independent.
                assert await page.evaluate('''async () => {
                  const {prepareTikzSvg} = await import('/vendor/tikzjax/study-svg.mjs');
                  const src='<svg xmlns="http://www.w3.org/2000/svg" width="20pt" onload="bad()"><script>bad()</script><foreignObject/><animate/><defs><path id="a"/></defs><use href="#a"/><image href="https://invalid.example/x"/><g fill="url(https://invalid.example/x)"/></svg>';
                  const a=prepareTikzSvg(src), b=prepareTikzSvg(src);
                  return !a.querySelector('script,foreignObject,animate,image') && !a.hasAttribute('onload')
                    && a.querySelector('use').getAttribute('href') === '#'+a.querySelector('path').id
                    && a.querySelector('path').id !== b.querySelector('path').id
                    && !a.querySelector('g').hasAttribute('fill') && a.getAttribute('width').endsWith('em');
                }''')
                assert not remote, remote
                assert not errors, errors
            finally:
                await browser.close()
    try:
        thread.start()
        asyncio.run(exercise())
    finally:
        server.should_exit = True
        thread.join(timeout=10)
        sock.close()
