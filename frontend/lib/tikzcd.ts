import remarkParse from 'remark-parse';
import remarkMath from 'remark-math';
import { unified } from 'unified';

export const DEFAULT_TIKZCD = String.raw`\begin{tikzcd}
A \arrow[r, "f"] \arrow[d, "g"'] & B \arrow[d, "h"] \\
C \arrow[r, "k"'] & D
\end{tikzcd}`;

export { macroPreamble } from '../vendor/tikzjax/study-svg.mjs';

export function tikzCdMarkdown(source: string) {
  const fence = '`'.repeat(Math.max(3, ...[...source.matchAll(/`+/g)].map((match) => match[0].length + 1)));
  return `${fence}tikzcd\n${source.trim()}\n${fence}`;
}

interface Node {
  type: string;
  lang?: string | null;
  value?: string;
  children?: Node[];
  position?: { start: { offset?: number }; end: { offset?: number } };
}

/** Dedicated fences and display math are editable; ordinary TeX/code examples stay literal. */
export function tikzCdAtCursor(markdown: string, anchor: number, head = anchor): { from: number; to: number; source: string; original: string } | null {
  let found: { from: number; to: number; source: string; original: string } | null = null;
  const visit = (node: Node) => {
    const from = node.position?.start.offset;
    const to = node.position?.end.offset;
    if (((node.type === 'code' && ['tikzcd', 'tikz-cd'].includes(node.lang || ''))
      || (node.type === 'math' && node.value?.includes('\\begin{tikzcd}')))
      && from !== undefined && to !== undefined && Math.min(anchor, head) >= from && Math.max(anchor, head) <= to) {
      found = { from, to, source: node.value || '', original: markdown.slice(from, to) };
    }
    node.children?.forEach(visit);
  };
  visit(unified().use(remarkParse).use(remarkMath).parse(markdown) as Node);
  return found;
}
