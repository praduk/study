import { decodeNamedCharacterReference } from 'decode-named-character-reference';

export const STUDY_REFERENCE_ATTRIBUTE = 'data-study-reference';

export interface StudyReferenceTextPart {
  kind: 'text' | 'reference';
  value: string;
}

interface MarkdownNode {
  type: string;
  value?: string;
  data?: Record<string, unknown>;
  position?: {
    start: { offset?: number };
    end: { offset?: number };
  };
  children?: MarkdownNode[];
}

interface StudyReferenceNode extends MarkdownNode {
  type: 'studyReference';
  literalTag: string;
  children: MarkdownNode[];
}

const REFERENCE_PATTERN = /@[a-z][a-z0-9-]*(?::[a-z][a-z0-9-]*)*/g;
const EMAIL_OR_IDENTIFIER_CHARACTER = /[\p{L}\p{N}\p{M}.!#$%&'*+/=?^_`{|}~@-]/u;
const TAG_CONTINUATION_CHARACTER = /[A-Za-z0-9:_-]/;
const MARKDOWN_ESCAPABLE = /[!"#$%&'()*+,\-./:;<=>?@[\\\]^_`{|}~]/;
const CHARACTER_REFERENCE = /^&(#(?:[xX][0-9a-fA-F]+|[0-9]+)|[A-Za-z][A-Za-z0-9]+);/;

function decodeNumericReference(value: string): string {
  const hexadecimal = value[1] === 'x' || value[1] === 'X';
  const digits = value.slice(hexadecimal ? 2 : 1);
  const codePoint = Number.parseInt(digits, hexadecimal ? 16 : 10);
  if (
    !Number.isFinite(codePoint) ||
    codePoint === 0 ||
    codePoint > 0x10ffff ||
    (codePoint >= 0xd800 && codePoint <= 0xdfff)
  ) {
    return '\uFFFD';
  }
  return String.fromCodePoint(codePoint);
}

/**
 * Locate rendered characters that did not originate as literal reference
 * syntax. Markdown removes a backslash from `\@tag`, and decodes character
 * references such as `&#64;tag`; neither form should become an active Study
 * reference after parsing.
 */
function nonLiteralReferenceStarts(raw: string, rendered: string): Set<number> {
  const protectedStarts = new Set<number>();
  let reconstructed = '';
  let rawIndex = 0;

  while (rawIndex < raw.length) {
    const outputIndex = reconstructed.length;
    const character = raw[rawIndex];
    const next = raw[rawIndex + 1];

    if (character === '\\' && next && MARKDOWN_ESCAPABLE.test(next)) {
      if (next === '@') protectedStarts.add(outputIndex);
      reconstructed += next;
      rawIndex += 2;
      continue;
    }

    if (character === '&') {
      const match = raw.slice(rawIndex).match(CHARACTER_REFERENCE);
      if (match) {
        const entity = match[1];
        const decoded = entity.startsWith('#')
          ? decodeNumericReference(entity)
          : decodeNamedCharacterReference(entity);
        if (decoded !== false) {
          if (decoded === '@') protectedStarts.add(outputIndex);
          reconstructed += decoded;
          rawIndex += match[0].length;
          continue;
        }
      }
    }

    const codePoint = raw.codePointAt(rawIndex);
    if (codePoint === undefined) break;
    const literal = String.fromCodePoint(codePoint);
    reconstructed += literal;
    rawIndex += literal.length;
  }

  // Positions are useful only if our small Markdown text decoder exactly
  // agrees with the parser. Fail closed when an unfamiliar transformation is
  // encountered so escaped syntax cannot accidentally become interactive.
  if (reconstructed !== rendered) {
    const fallback = new Set<number>();
    if (raw.includes('\\@')) {
      const pattern = new RegExp(
        REFERENCE_PATTERN.source,
        REFERENCE_PATTERN.flags,
      );
      for (const match of rendered.matchAll(pattern)) {
        fallback.add(match.index ?? 0);
      }
    }
    return fallback;
  }
  return protectedStarts;
}

/**
 * Split prose into literal text and possible Study references.
 *
 * This intentionally recognizes the full family of relative and canonical
 * tags. Resolution, including ambiguity, remains the server's responsibility.
 */
export function splitStudyReferenceText(
  value: string,
  nonLiteralStarts: ReadonlySet<number> = new Set(),
): StudyReferenceTextPart[] {
  const parts: StudyReferenceTextPart[] = [];
  const pattern = new RegExp(REFERENCE_PATTERN.source, REFERENCE_PATTERN.flags);
  let cursor = 0;

  for (const match of value.matchAll(pattern)) {
    const index = match.index ?? 0;
    const literalTag = match[0];
    const previous = value[index - 1];
    const next = value[index + literalTag.length];

    // Do not reinterpret addresses/identifiers such as person@example.com,
    // or the valid prefix of an invalid tag.
    if (
      nonLiteralStarts.has(index) ||
      previous === '\\' ||
      (previous !== undefined &&
        EMAIL_OR_IDENTIFIER_CHARACTER.test(previous)) ||
      (next !== undefined && TAG_CONTINUATION_CHARACTER.test(next))
    ) {
      continue;
    }

    if (index > cursor)
      parts.push({ kind: 'text', value: value.slice(cursor, index) });
    parts.push({ kind: 'reference', value: literalTag });
    cursor = index + literalTag.length;
  }

  if (cursor < value.length || parts.length === 0) {
    parts.push({ kind: 'text', value: value.slice(cursor) });
  }

  return parts;
}

function referenceNode(literalTag: string): StudyReferenceNode {
  return {
    type: 'studyReference',
    literalTag,
    data: {
      hName: 'span',
      hProperties: { [STUDY_REFERENCE_ATTRIBUTE]: literalTag },
    },
    children: [{ type: 'text', value: literalTag }],
  };
}

const EXCLUDED_SUBTREES = new Set([
  'code',
  'inlineCode',
  'math',
  'inlineMath',
  'link',
  'linkReference',
]);

/** Transform only Markdown prose nodes; code, math, and link subtrees are left intact. */
export function transformStudyReferences(
  tree: MarkdownNode,
  source = '',
): void {
  if (EXCLUDED_SUBTREES.has(tree.type) || !tree.children) return;

  const children: MarkdownNode[] = [];
  for (const child of tree.children) {
    if (child.type !== 'text' || child.value === undefined) {
      transformStudyReferences(child, source);
      children.push(child);
      continue;
    }

    const start = child.position?.start.offset;
    const end = child.position?.end.offset;
    const raw =
      source && start !== undefined && end !== undefined
        ? source.slice(start, end)
        : child.value;
    const parts = splitStudyReferenceText(
      child.value,
      nonLiteralReferenceStarts(raw, child.value),
    );
    if (!parts.some((part) => part.kind === 'reference')) {
      children.push(child);
      continue;
    }

    for (const part of parts) {
      children.push(
        part.kind === 'reference'
          ? referenceNode(part.value)
          : { type: 'text', value: part.value },
      );
    }
  }

  tree.children = children;
}

/**
 * Remark plugin for Study's @tag syntax. Install it after remark-math and
 * remarkStudyMath so TeX has already been isolated from prose.
 */
export function remarkStudyReferences() {
  return (tree: MarkdownNode, file: { value?: string | Uint8Array }) => {
    const source =
      typeof file.value === 'string'
        ? file.value
        : file.value
          ? new TextDecoder().decode(file.value)
          : '';
    transformStudyReferences(tree, source);
  };
}
