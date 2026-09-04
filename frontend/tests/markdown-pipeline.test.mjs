import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';

import React from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import remarkParse from 'remark-parse';
import { unified } from 'unified';

import {
  mathJaxMarkdownHandlers,
  normalizeMathJaxDelimiters,
  remarkStudyMath,
} from '../lib/markdown-math.ts';
import { readingVariantSelection } from '../lib/reference-navigation.ts';
import {
  remarkStudyDiagrams,
  STUDY_COMMUTATIVE_ATTRIBUTE,
} from '../lib/remark-study-diagrams.ts';
import { remarkStudyReferences } from '../lib/remark-study-references.ts';

function renderMarkdown(source) {
  return renderToStaticMarkup(
    React.createElement(
      ReactMarkdown,
      {
        remarkPlugins: [
          remarkGfm,
          remarkMath,
          remarkStudyMath,
          remarkStudyReferences,
          remarkStudyDiagrams,
        ],
        remarkRehypeOptions: { handlers: mathJaxMarkdownHandlers },
        components: {
          div({ children, ...props }) {
            return props[STUDY_COMMUTATIVE_ATTRIBUTE]
              ? React.createElement('figure', {
                  'data-rendered-diagram': props[STUDY_COMMUTATIVE_ATTRIBUTE],
                })
              : React.createElement('div', props, children);
          },
        },
      },
      normalizeMathJaxDelimiters(source),
    ),
  );
}

test('TeX survives the Markdown pipeline verbatim', () => {
  const source = String.raw`Inline $\{x_1\}+\RR$ and slash \(y_2+\RR\), with a literal \$5.

$$
\begin{aligned}
a_1 &= b \\
c &= d
\end{aligned}
$$

Same-line display: $$X_2$$. Slash display: \[\{z_3\}\].`;
  const html = renderMarkdown(source);

  assert.match(html, /\\\(\\\{x_1\\\}\+\\RR\\\)/);
  assert.match(html, /\\\(y_2\+\\RR\\\)/);
  assert.match(html, /literal \\\u00245/);
  assert.match(html, /\\\[X_2\\\]/);
  assert.match(html, /\\\[\\\{z_3\\\}\\\]/);
  assert.ok(
    html.includes(String.raw`a_1 &amp;= b \\
c &amp;= d`),
  );
});

test('inline MathJax SVGs are not forced into block layout', () => {
  const css = readFileSync(new URL('../app/globals.css', import.meta.url), 'utf8');
  assert.match(
    css,
    /\.math-inline-source\s+mjx-container\s*>\s*svg\s*\{\s*display:\s*inline;/,
  );
});

test('slash delimiters are not rewritten inside code', () => {
  const inlineCode = '`\\(not_math\\)`';
  const fencedCode = '```tex\n\\[not_math\\]\n```';
  const source = `${inlineCode}\n\n${fencedCode}`;

  assert.equal(normalizeMathJaxDelimiters(source), source);
  const html = renderMarkdown(source);
  assert.match(html, /<code>\\\(not_math\\\)<\/code>/);
  assert.match(html, /<code class="language-tex">\\\[not_math\\\]/);
});

test('slash delimiters stay literal in every Markdown code block form', () => {
  const source = [String.raw`Outside \(math\).

    \(indented_code\)

>     \[quoted_indented_code\]

~~~tex
\(tilde_fenced_code\)
~~~`,
  'An opener \\(does not cross `inline code` to a later closer\\).'].join('\n\n');
  const normalized = normalizeMathJaxDelimiters(source);

  assert.match(normalized, /Outside \$math\$\./);
  assert.match(normalized, /\\\(indented_code\\\)/);
  assert.match(normalized, /\\\[quoted_indented_code\\\]/);
  assert.match(normalized, /\\\(tilde_fenced_code\\\)/);
  assert.match(
    normalized,
    /An opener \\\(does not cross `inline code` to a later closer\\\)\./,
  );
});

test('@tags are recognized only in Markdown prose', async () => {
  const tick = '`';
  const source = [
    'See @group and @math:algebra:th:lagrange.',
    'Email person@example.com.',
    'International email josé@example.com.',
    'Greek email δοκιμή@example.com.',
    `Code ${tick}@not-code${tick}.`,
    '[Link @not-link](https://example.com/@not-url).',
    'Math $@not_math$.',
    `${tick}${tick}${tick}text`,
    '@not-fenced',
    `${tick}${tick}${tick}`,
  ].join('\n\n');
  const processor = unified()
    .use(remarkParse)
    .use(remarkMath)
    .use(remarkStudyReferences);
  const tree = await processor.run(processor.parse(source));
  const references = [];
  const walk = (node) => {
    if (node.type === 'studyReference') references.push(node.literalTag);
    for (const child of node.children ?? []) walk(child);
  };
  walk(tree);

  assert.deepEqual(references, ['@group', '@math:algebra:th:lagrange']);
});

test('escaped and entity-encoded @tags stay literal', async () => {
  const source = String.raw`Escaped \@group. Entity &#64;ring. Named &commat;field. Active @module.`;
  const processor = unified()
    .use(remarkParse)
    .use(remarkMath)
    .use(remarkStudyReferences);
  const tree = await processor.run(processor.parse(source), { value: source });
  const references = [];
  const walk = (node) => {
    if (node.type === 'studyReference') references.push(node.literalTag);
    for (const child of node.children ?? []) walk(child);
  };
  walk(tree);

  assert.deepEqual(references, ['@module']);
  const html = renderMarkdown(source);
  assert.match(html, /Escaped @group/);
  assert.doesNotMatch(html, /data-study-reference="@group"/);
  assert.doesNotMatch(html, /data-study-reference="@ring"/);
  assert.doesNotMatch(html, /data-study-reference="@field"/);
  assert.match(html, /data-study-reference="@module"/);
});

test('commutative diagram tokens render only from Markdown prose', () => {
  const id = 'a'.repeat(32);
  const token = `[[commutative:${id}|width=61]]`;
  const source = [
    `Visible ${token} after.`,
    `Inline \`${token}\`.`,
    `    ${token}`,
    `~~~text\n${token}\n~~~`,
    `Math $${token}$.`,
  ].join('\n\n');
  const html = renderMarkdown(source);

  assert.equal((html.match(/data-rendered-diagram=/g) ?? []).length, 1);
  assert.ok(html.includes(`<code>${token}</code>`));
  assert.equal((html.match(/commutative:/g) ?? []).length, 4);
});

test('exact reference variants select their formulation or supplement', () => {
  const entry = {
    formulations: [
      { id: 'main-form', main: true },
      { id: 'category-form', main: false },
    ],
    supplements: [
      { id: 'main-proof', main: true },
      { id: 'action-proof', main: false },
    ],
  };

  assert.deepEqual(readingVariantSelection(entry, 'category-form'), {
    formulationId: 'category-form',
    supplementId: null,
  });
  assert.deepEqual(readingVariantSelection(entry, 'action-proof'), {
    formulationId: 'main-form',
    supplementId: 'action-proof',
  });
  assert.deepEqual(readingVariantSelection(entry, 'unknown'), {
    formulationId: 'main-form',
    supplementId: null,
  });
});
