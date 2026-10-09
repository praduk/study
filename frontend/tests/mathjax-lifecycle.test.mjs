import assert from 'node:assert/strict';
import test from 'node:test';

import {
  clearMathJax,
  configureMathJax,
  typesetWithMathJax,
} from '../lib/mathjax.ts';

test('MathJax cleanup is serialized after typesetting an owned DOM island', async () => {
  const calls = [];
  globalThis.window = {
    MathJax: {
      startup: { promise: Promise.resolve() },
      typesetClear(elements) { calls.push(['clear', elements]); },
      async typesetPromise(elements) { calls.push(['typeset', elements]); },
    },
  };
  globalThis.document = { getElementById() { return {}; } };
  const element = { isConnected: true };

  try {
    configureMathJax({});
    await typesetWithMathJax(element);
    await clearMathJax(element);
  } finally {
    delete globalThis.document;
    delete globalThis.window;
  }

  assert.deepEqual(calls.map(([operation]) => operation), ['clear', 'typeset', 'clear']);
  assert.ok(calls.every(([_operation, elements]) => elements[0] === element));
});

test('equation SVG conversion shares the typesetting queue and rejects invalid TeX', async () => {
  const { renderEquationSvg } = await import('../lib/mathjax.ts');
  const calls = [];
  let removed = 0;
  globalThis.window = { MathJax: {
    startup: { promise: Promise.resolve() },
    typesetClear() {},
    async typesetPromise() { calls.push('typeset'); },
    async tex2svgPromise(latex) {
      calls.push(latex);
      const svg = {
        style: {},
        querySelector() { return latex === 'bad' ? { getAttribute() { return 'Unknown command'; } } : null; },
        getBoundingClientRect() { return { width: 123.5, height: 42.2 }; },
        setAttribute(name, value) { calls.push(`${name}=${value}`); },
      };
      return { style: {}, querySelector() { return svg; }, remove() { removed++; } };
    },
  } };
  globalThis.document = { getElementById() { return {}; }, body: { appendChild() {} } };
  globalThis.XMLSerializer = class { serializeToString() { return '<svg/>'; } };
  try {
    configureMathJax({ R: '\\mathbb{R}', norm: ['\\lVert#1\\rVert', 1] });
    const typeset = typesetWithMathJax({ isConnected: true });
    const conversion = renderEquationSvg('\\norm{x} \\in \\R');
    await typeset;
    assert.deepEqual(await conversion, { svg: '<svg/>', width: 124, height: 43 });
    assert.equal(calls[0], 'typeset');
    assert.equal(calls[1], '\\norm{x} \\in \\R');
    await assert.rejects(renderEquationSvg('bad'), /Unknown command/);
    assert.equal((await renderEquationSvg('x')).width, 124);
    assert.equal(removed, 2);
  } finally {
    delete globalThis.window;
    delete globalThis.document;
    delete globalThis.XMLSerializer;
  }
});
