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
