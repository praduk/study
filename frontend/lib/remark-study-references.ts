import { decodeNamedCharacterReference } from 'decode-named-character-reference';

export const STUDY_REFERENCE_ATTRIBUTE = 'data-study-reference';
export const STUDY_REFERENCE_SOURCE_ATTRIBUTE = 'data-study-reference-source';
export const STUDY_REFERENCE_LABEL_ATTRIBUTE = 'data-study-reference-label';

export type StudyReferenceTextPart =
  | { kind: 'text'; value: string }
  | {
      kind: 'reference';
      value: string;
      literalTag: string;
      replacementText?: string;
    };

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
  sourceText: string;
  replacementText?: string;
  children: MarkdownNode[];
}

const REFERENCE_PATTERN = /@(?:\[([^\x5b\x5d\r\n]+)\])?([a-z][a-z0-9-]*(?::[a-z][a-z0-9-]*)*)/g;
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
      if (next === '@' || next === '[' || next === ']') {
        protectedStarts.add(outputIndex);
      }
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
          if (decoded === '@' || decoded === '[' || decoded === ']') {
            protectedStarts.add(outputIndex);
          }
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
    const pattern = new RegExp(
      REFERENCE_PATTERN.source,
      REFERENCE_PATTERN.flags,
    );
    for (const match of rendered.matchAll(pattern)) {
      fallback.add(match.index ?? 0);
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
    const sourceText = match[0];
    const hasReplacementText = match[1] !== undefined;
    const replacementText = match[1]?.trim();
    const literalTag = `@${match[2]}`;
    const previous = value[index - 1];
    const next = value[index + sourceText.length];
    const closingBracket = hasReplacementText
      ? index + sourceText.indexOf(']')
      : -1;

    // Do not reinterpret addresses/identifiers such as person@example.com,
    // or the valid prefix of an invalid tag.
    if (
      (hasReplacementText && !replacementText) ||
      nonLiteralStarts.has(index) ||
      (hasReplacementText &&
        (nonLiteralStarts.has(index + 1) ||
          nonLiteralStarts.has(closingBracket))) ||
      previous === '\\' ||
      (previous !== undefined &&
        EMAIL_OR_IDENTIFIER_CHARACTER.test(previous)) ||
      (next !== undefined && TAG_CONTINUATION_CHARACTER.test(next))
    ) {
      continue;
    }

    if (index > cursor)
      parts.push({ kind: 'text', value: value.slice(cursor, index) });
    parts.push({
      kind: 'reference',
      value: sourceText,
      literalTag,
      ...(replacementText ? { replacementText } : {}),
    });
    cursor = index + sourceText.length;
  }

  if (cursor < value.length || parts.length === 0) {
    parts.push({ kind: 'text', value: value.slice(cursor) });
  }

  return parts;
}

function referenceNode(
  sourceText: string,
  literalTag: string,
  replacementText?: string,
): StudyReferenceNode {
  return {
    type: 'studyReference',
    literalTag,
    sourceText,
    ...(replacementText ? { replacementText } : {}),
    data: {
      hName: 'span',
      hProperties: {
        [STUDY_REFERENCE_ATTRIBUTE]: literalTag,
        [STUDY_REFERENCE_SOURCE_ATTRIBUTE]: sourceText,
        ...(replacementText
          ? { [STUDY_REFERENCE_LABEL_ATTRIBUTE]: replacementText }
          : {}),
      },
    },
    children: [{ type: 'text', value: sourceText }],
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
          ? referenceNode(
              part.value,
              part.literalTag,
              part.replacementText,
            )
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
