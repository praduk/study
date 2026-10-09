import assert from 'node:assert/strict';
import test from 'node:test';
import { DEFAULT_TIKZCD, macroPreamble, tikzCdAtCursor, tikzCdMarkdown } from '../lib/tikzcd.ts';
import { mathJaxOptions } from '../lib/mathjax-options.mjs';
import extensions from '../../study_app/mathjax_extensions.json' with { type: 'json' };
import { svgPictureMarkers } from '../vendor/tikzjax/study-picture-markers.mjs';

test('empty nested pictures keep one balanced SVG root across DVI specials', () => {
  const machine = { svgDepth: 0, paperwidth: 120, paperheight: 80 };
  const parts = [
    '<svg beginpicture><g>',
    '<svg beginpicture><g></g></svg endpicture><svg beginpicture>',
    '<text>A</text></svg endpicture>',
    '<svg beginpicture></svg endpicture></g></svg endpicture>',
  ];
  const output = parts.map(source => svgPictureMarkers(source, machine)).join('');
  assert.equal(machine.svgDepth, 0);
  assert.equal((output.match(/<svg\b/g) || []).length, 1);
  assert.equal((output.match(/<\/svg>/g) || []).length, 1);
  assert.ok(output.endsWith('<g></g><text>A</text></g></svg>'));
  assert.ok(!output.includes('beginpicture') && !output.includes('endpicture'));
  assert.throws(() => svgPictureMarkers('</svg endpicture>', machine), /Unbalanced/);
});

test('TikZ-CD editing selects only the containing dedicated code fence', () => {
  const block = tikzCdMarkdown(DEFAULT_TIKZCD);
  const source = `Before.\n\n${block}\n\nAfter.`;
  const target = tikzCdAtCursor(source, source.indexOf('begin{tikzcd}'));
  assert.equal(target.original, block);
  assert.equal(target.source.trim(), DEFAULT_TIKZCD);
  assert.equal(source.slice(0, target.from), 'Before.\n\n');
  assert.equal(source.slice(target.to), '\n\nAfter.');
  assert.equal(tikzCdAtCursor(source, 0), null);
  assert.equal(tikzCdAtCursor('```latex\n'+DEFAULT_TIKZCD+'\n```', 20), null);
  assert.equal(tikzCdAtCursor('`'+DEFAULT_TIKZCD+'`', 2), null);
  assert.equal(tikzCdAtCursor(block.replace('tikzcd\n', 'tikz-cd\n'), 20).source.trim(), DEFAULT_TIKZCD);
});

test('diagram fences protect embedded backticks and preserve TikZ syntax', () => {
  const code = DEFAULT_TIKZCD.replace('\\end{tikzcd}', '{A`B}\n\\end{tikzcd}');
  const block = tikzCdMarkdown(code);
  assert.equal(tikzCdAtCursor(block, 20).source.trim(), code);
  const longer = tikzCdMarkdown(code + '\n% ``` is a comment');
  assert.ok(longer.startsWith('````tikzcd\n'));
});

test('new diagrams start with an empty TikZ-CD environment', () => {
  assert.equal(DEFAULT_TIKZCD, '\\begin{tikzcd}\n\\end{tikzcd}');
});

test('shared macros become scoped-compatible LaTeX definitions with exact arities', () => {
  const preamble = macroPreamble({ R: '\\mathbb{R}', pair: ['(#1,#2)', 2], optional: ['#1+#2', 2, 'x'] });
  assert.ok(preamble.includes('\\providecommand{\\R}{}\\renewcommand{\\R}{\\mathbb{R}}'));
  assert.ok(preamble.includes('\\renewcommand{\\pair}[2]{(#1,#2)}'));
  assert.ok(preamble.includes('\\renewcommand{\\optional}[2][x]{#1+#2}'));
});

test('MathJax extension configuration stays local and preserves explicit compatibility choices', () => {
  const macros = { R: '\\mathbb{R}' };
  const config = mathJaxOptions(macros);
  assert.equal(config.tex.macros, macros);
  assert.deepEqual(config.tex.packages['[+]'], extensions.enabled);
  assert.ok(config.loader.load.includes('[tex]/amscd'));
  assert.ok(config.loader.load.includes('[tex]/mathtools'));
  assert.ok(config.loader.load.includes('[tex]/mhchem'));
  for (const name of [...extensions.disabled, ...extensions.explicit]) {
    assert.ok(!config.loader.load.includes(`[tex]/${name}`));
  }
  assert.ok(Object.values(config.loader.paths).every(path => path.startsWith('/vendor/')));
});

test('display-math TikZ-CD can be reopened and replaced as one block', () => {
  const block = '$$\n'+DEFAULT_TIKZCD+'\n$$';
  const target = tikzCdAtCursor('Before\n\n'+block+'\n\nAfter', 20);
  assert.equal(target.source.trim(), DEFAULT_TIKZCD);
  assert.equal(target.original, block);
});
