from __future__ import annotations

import asyncio
import json
import socket
import threading
from itertools import pairwise

import pytest
import uvicorn

from study_app.app import create_app


@pytest.mark.parametrize('theme', ['light', 'dark'])
@pytest.mark.parametrize('phone', [False, True], ids=['desktop', 'phone'])
def test_packaged_statement_and_proof_heading_hierarchy(settings_factory, theme, phone):
    """Tailwind must not flatten authored headings or let prompt styling override them."""
    playwright_api = pytest.importorskip('playwright.async_api')
    settings = settings_factory()
    app = create_app(settings, local_mode=True)
    store = app.state.store
    folder = store.create_folder('Heading checks', 'heading-checks', None)

    def content(label):
        return '\n\n'.join(
            f'{"#" * level} {label} level {level}'
            '\n\nBody text with $x^2$.'
            for level in range(1, 7)
        ) + '\n\nSetext heading\n==============\n\nA final paragraph.'

    entry = store.create_entry(
        folder['id'], 'th', 'Heading fixture', 'fixture', '', content('Statement'),
        review_enabled=False,
    )
    store.add_supplement(entry['id'], {
        'kind': 'pf', 'label': 'Main', 'main': True, 'subtag': None,
        'content': content('Proof'),
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
            page = await browser.new_page(
                viewport={'width': 390 if phone else 1440, 'height': 844 if phone else 1000},
                is_mobile=phone, has_touch=phone,
            )
            errors = []
            page.on('pageerror', lambda error: errors.append(str(error)))
            await page.add_init_script(f"localStorage.setItem('study-theme', '{theme}')")
            try:
                await page.goto(f'http://127.0.0.1:{port}/library/heading-checks/th/fixture')
                await playwright_api.expect(page.get_by_role('heading', name='Statement level 1')).to_be_visible()
                await page.locator('.supplement-list mjx-container svg').first.wait_for()
                metrics = {}
                for name, selector in {
                    'statement': '.reading-pane > .markdown-body',
                    'proof': '.supplement-list .markdown-body',
                }.items():
                    block = page.locator(selector)
                    metrics[name] = await block.evaluate('''(block) => {
                      const style = getComputedStyle(block);
                      return {
                        bodySize: parseFloat(style.fontSize),
                        foreground: style.color,
                        headings: [...block.querySelectorAll('h1,h2,h3,h4,h5,h6')].map(h => {
                          const s = getComputedStyle(h), r = h.getBoundingClientRect();
                          return {tag: h.tagName, size: parseFloat(s.fontSize), weight: Number(s.fontWeight),
                            color: s.color, marginTop: parseFloat(s.marginTop), width: r.width};
                        }),
                        overflow: block.scrollWidth > block.clientWidth,
                      };
                    }''')
                    headings = metrics[name]['headings']
                    assert [h['tag'] for h in headings] == ['H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'H1']
                    assert all(a['size'] > b['size'] for a, b in pairwise(headings[:6]))
                    assert headings[0]['size'] > metrics[name]['bodySize'] * 1.5
                    assert headings[0]['marginTop'] == 0
                    assert all(h['weight'] >= 600 for h in headings)
                    assert all(h['color'] == metrics[name]['foreground'] for h in headings)
                    assert not metrics[name]['overflow']
                    await block.locator('h1').first.scroll_into_view_if_needed()
                    await page.screenshot(path=str(settings.root / f'{name}-{theme}.png'))
                assert await page.evaluate('document.documentElement.scrollWidth <= innerWidth')
                assert not errors
                (settings.root / 'heading-metrics.json').write_text(json.dumps(metrics, indent=2))
            finally:
                await browser.close()

    try:
        thread.start()
        asyncio.run(exercise())
    finally:
        server.should_exit = True
        thread.join(timeout=10)
        sock.close()
