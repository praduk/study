import remarkParse from 'remark-parse';
import { unified } from 'unified';

interface Position {
  start: { offset?: number };
  end: { offset?: number };
}

interface MarkdownNode {
  type: string;
  value?: string;
  data?: Record<string, unknown>;
  position?: Position;
  children?: MarkdownNode[];
}

interface MathNode extends MarkdownNode {
  value: string;
}

interface SourceRange {
  start: number;
  end: number;
}

const markdownParser = unified().use(remarkParse);

function codeRanges(source: string): SourceRange[] {
  const ranges: SourceRange[] = [];
  const tree = markdownParser.parse(source) as MarkdownNode;

  const collect = (node: MarkdownNode) => {
    if ((node.type === 'code' || node.type === 'inlineCode') && node.position) {
      const start = node.position.start.offset;
      const end = node.position.end.offset;
      if (start !== undefined && end !== undefined) ranges.push({ start, end });
      return;
    }
    node.children?.forEach(collect);
  };

  collect(tree);
  return ranges.sort((left, right) => left.start - right.start);
}

function isEscaped(source: string, index: number) {
  let backslashes = 0;
  for (
    let cursor = index - 1;
    cursor >= 0 && source[cursor] === '\\';
    cursor -= 1
  )
    backslashes += 1;
  return backslashes % 2 === 1;
}

function delimiterEnd(
  source: string,
  start: number,
  close: string,
  multiline: boolean,
  protectedRanges: SourceRange[],
) {
  let rangeIndex = 0;
  for (let index = start; index < source.length - 1; index += 1) {
    while (
      rangeIndex < protectedRanges.length &&
      protectedRanges[rangeIndex].end <= index
    ) {
      rangeIndex += 1;
    }
    const range = protectedRanges[rangeIndex];
    // A delimiter may not cross a Markdown code node. Treat such an opener as
    // ordinary prose rather than allowing a later closer to consume the code.
    if (range && range.start <= index && index < range.end) return -1;
    if (!multiline && source[index] === '\n') return -1;
    if (source.startsWith(close, index) && !isEscaped(source, index))
      return index;
  }
  return -1;
}

/** Convert MathJax's slash delimiters into remark-math syntax outside code. */
export function normalizeMathJaxDelimiters(source: string) {
  const protectedRanges = codeRanges(source);
  let result = '';
  let index = 0;
  let rangeIndex = 0;

  while (index < source.length) {
    while (
      rangeIndex < protectedRanges.length &&
      protectedRanges[rangeIndex].end <= index
    ) {
      rangeIndex += 1;
    }
    const range = protectedRanges[rangeIndex];
    if (range && range.start <= index && index < range.end) {
      result += source.slice(index, range.end);
      index = range.end;
      continue;
    }

    const inline = source.startsWith('\\(', index) && !isEscaped(source, index);
    const display =
      source.startsWith('\\[', index) && !isEscaped(source, index);
    if (inline || display) {
      const close = inline ? '\\)' : '\\]';
      const end = delimiterEnd(
        source,
        index + 2,
        close,
        display,
        protectedRanges,
      );
      if (end !== -1) {
        const dollars = display ? '$$' : '$';
        result += `${dollars}${source.slice(index + 2, end)}${dollars}`;
        index = end + 2;
        continue;
      }
    }

    const character = source[index];
    result += character;
    index += 1;
  }

  return result;
}

function visit(node: MarkdownNode, source: string) {
  if (node.type === 'inlineMath' && node.position) {
    const start = node.position.start.offset;
    const end = node.position.end.offset;
    if (
      start !== undefined &&
      end !== undefined &&
      source.slice(start, end).startsWith('$$')
    ) {
      node.data = { ...node.data, studyDisplayMath: true };
    }
  }

  // Markdown consumes the backslash in `\$`. Put it back so MathJax's
  // processEscapes option treats the dollar as prose instead of a delimiter.
  if (node.type === 'text' && node.value !== undefined && node.position) {
    const start = node.position.start.offset;
    const end = node.position.end.offset;
    if (start !== undefined && end !== undefined) {
      const raw = source.slice(start, end);
      const escapedDollarOrdinals = new Set<number>();
      let dollarOrdinal = 0;
      for (let index = 0; index < raw.length; index += 1) {
        if (raw[index] !== '$') continue;
        let backslashes = 0;
        for (
          let cursor = index - 1;
          cursor >= 0 && raw[cursor] === '\\';
          cursor -= 1
        )
          backslashes += 1;
        if (backslashes % 2 === 1) escapedDollarOrdinals.add(dollarOrdinal);
        dollarOrdinal += 1;
      }
      if (escapedDollarOrdinals.size) {
        dollarOrdinal = 0;
        node.value = node.value.replaceAll('$', () => {
          const escaped = escapedDollarOrdinals.has(dollarOrdinal);
          dollarOrdinal += 1;
          return escaped ? '\\$' : '$';
        });
      }
    }
  }

  node.children?.forEach((child) => visit(child, source));
}

/** Preserve TeX before Markdown can interpret its backslashes and punctuation. */
export function remarkStudyMath() {
  return (tree: MarkdownNode, file: { value?: string | Uint8Array }) => {
    const source =
      typeof file.value === 'string'
        ? file.value
        : new TextDecoder().decode(file.value);
    visit(tree, source);
  };
}

function mathElement(node: MathNode, display: boolean) {
  return {
    type: 'element' as const,
    // A same-line `$$...$$` node is inline in the Markdown tree, so keep a
    // phrasing wrapper even though MathJax renders it in display mode.
    tagName: node.type === 'math' ? 'div' : 'span',
    properties: {
      className: [
        'math-source',
        display ? 'math-display-source' : 'math-inline-source',
      ],
    },
    children: [
      {
        type: 'text' as const,
        value: display ? `\\[${node.value}\\]` : `\\(${node.value}\\)`,
      },
    ],
  };
}

/** Emit delimiters as text nodes so the locally served MathJax runtime can typeset them. */
export const mathJaxMarkdownHandlers = {
  inlineMath(_state: unknown, node: MathNode) {
    return mathElement(node, node.data?.studyDisplayMath === true);
  },
  math(_state: unknown, node: MathNode) {
    return mathElement(node, true);
  },
};
