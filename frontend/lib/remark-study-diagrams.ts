export const STUDY_COMMUTATIVE_ATTRIBUTE = 'data-study-commutative';
export const STUDY_COMMUTATIVE_WIDTH_ATTRIBUTE = 'data-study-width';

interface MarkdownNode {
  type: string;
  value?: string;
  data?: Record<string, unknown>;
  children?: MarkdownNode[];
}

interface DiagramMatch {
  start: number;
  end: number;
  id: string;
  width: number;
}

const DIAGRAM_PATTERN =
  /\[\[commutative:([a-f0-9]{32})(?:\|width=(\d{1,3}))?\]\]/g;

function diagramMatches(value: string): DiagramMatch[] {
  const matches: DiagramMatch[] = [];
  const pattern = new RegExp(DIAGRAM_PATTERN.source, DIAGRAM_PATTERN.flags);
  for (const match of value.matchAll(pattern)) {
    const start = match.index ?? 0;
    matches.push({
      start,
      end: start + match[0].length,
      id: match[1],
      width: Math.min(100, Math.max(10, Number(match[2] || 76))),
    });
  }
  return matches;
}

function diagramNode(match: DiagramMatch): MarkdownNode {
  return {
    type: 'studyCommutativeDiagram',
    data: {
      hName: 'div',
      hProperties: {
        [STUDY_COMMUTATIVE_ATTRIBUTE]: match.id,
        [STUDY_COMMUTATIVE_WIDTH_ATTRIBUTE]: String(match.width),
      },
    },
  };
}

/**
 * Split a paragraph around direct prose diagram tokens. Because code nodes are
 * never paragraphs, fenced, indented, and inline code remain literal. Tokens
 * inside links, math, or other nested phrasing are also deliberately literal.
 */
function splitParagraph(paragraph: MarkdownNode): MarkdownNode[] {
  const output: MarkdownNode[] = [];
  let phrasing: MarkdownNode[] = [];

  const flushPhrasing = () => {
    if (!phrasing.length) return;
    output.push({ ...paragraph, children: phrasing });
    phrasing = [];
  };

  for (const child of paragraph.children ?? []) {
    if (child.type !== 'text' || child.value === undefined) {
      phrasing.push(child);
      continue;
    }

    const matches = diagramMatches(child.value);
    if (!matches.length) {
      phrasing.push(child);
      continue;
    }

    let cursor = 0;
    for (const match of matches) {
      if (match.start > cursor) {
        phrasing.push({ type: 'text', value: child.value.slice(cursor, match.start) });
      }
      flushPhrasing();
      output.push(diagramNode(match));
      cursor = match.end;
    }
    if (cursor < child.value.length) {
      phrasing.push({ type: 'text', value: child.value.slice(cursor) });
    }
  }

  flushPhrasing();
  return output.length ? output : [paragraph];
}

const EXCLUDED_SUBTREES = new Set([
  'code',
  'inlineCode',
  'math',
  'inlineMath',
  'link',
  'linkReference',
]);

/** Transform prose diagram tokens only after Markdown has identified code. */
export function transformStudyDiagrams(tree: MarkdownNode): void {
  if (EXCLUDED_SUBTREES.has(tree.type) || !tree.children) return;

  for (const child of tree.children) transformStudyDiagrams(child);

  tree.children = tree.children.flatMap((child) =>
    child.type === 'paragraph' ? splitParagraph(child) : [child],
  );
}

export function remarkStudyDiagrams() {
  return (tree: MarkdownNode) => transformStudyDiagrams(tree);
}
