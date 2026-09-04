'use client';

import { useEffect, useState, type ReactNode } from 'react';

import {
  Popover,
  PopoverContent,
  PopoverDescription,
  PopoverHeader,
  PopoverTitle,
  PopoverTrigger,
} from '@/components/ui/popover';
import { api } from '@/lib/api';
import { referenceDisplayText } from '@/lib/reference-display';
import { cn } from '@/lib/utils';

export type StudyReferenceStatus =
  | 'resolved'
  | 'missing'
  | 'ambiguous'
  | 'unavailable';

export interface StudyReferenceTarget {
  entryId?: string;
  variantId?: string;
  folderId?: string;
  folderNamespace?: string;
  canonicalTag?: string;
  title?: string;
  kind?: string;
  label?: string;
  targetType?: string;
  header?: string;
  preview?: string;
}

export interface StudyReferenceResolution {
  status: StudyReferenceStatus;
  target?: StudyReferenceTarget;
  candidates?: StudyReferenceTarget[];
  message?: string;
}

export interface StudyReferenceProps {
  literalTag: string;
  currentFolderId: string;
  className?: string;
  onActivate?: (target: StudyReferenceTarget) => void;
  renderPreview?: (content: string, target: StudyReferenceTarget) => ReactNode;
  resolveReference?: (
    folderId: string,
    tag: string,
  ) => Promise<StudyReferenceResolution>;
}

type UnknownRecord = Record<string, unknown>;

function asRecord(value: unknown): UnknownRecord | undefined {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
    ? (value as UnknownRecord)
    : undefined;
}

function firstString(
  records: (UnknownRecord | undefined)[],
  ...keys: string[]
): string | undefined {
  for (const record of records) {
    if (!record) continue;
    for (const key of keys) {
      const value = record[key];
      if (typeof value === 'string' && value.trim()) return value;
    }
  }
  return undefined;
}

function parseTarget(
  value: unknown,
  fallback?: UnknownRecord,
): StudyReferenceTarget | undefined {
  const target = asRecord(value);
  const previewRecord =
    asRecord(target?.preview) ?? asRecord(fallback?.preview);
  const records = [target, previewRecord, fallback];
  const result: StudyReferenceTarget = {
    entryId: firstString(records, 'entry_id', 'entryId', 'id'),
    variantId: firstString(records, 'variant_id', 'variantId'),
    folderId: firstString(records, 'folder_id', 'folderId'),
    folderNamespace: firstString(records, 'folder_namespace', 'folderNamespace'),
    canonicalTag: firstString(records, 'canonical_tag', 'canonicalTag'),
    title: firstString(records, 'title'),
    kind: firstString(records, 'kind'),
    label: firstString(records, 'label'),
    targetType: firstString(records, 'target_type', 'targetType'),
    header: firstString(records, 'header'),
    preview: firstString(
      records,
      'preview',
      'summary',
      'excerpt',
      'body',
      'content',
    ),
  };

  return Object.values(result).some((item) => item !== undefined)
    ? result
    : undefined;
}

/** Normalize the small set of fields the preview consumes; unknown fields are ignored. */
export function normalizeStudyReferenceResolution(
  payload: unknown,
): StudyReferenceResolution {
  const root = asRecord(payload);
  if (!root) {
    return {
      status: 'unavailable',
      message: 'Reference could not be verified.',
    };
  }
  const status = root?.status;
  if (status !== 'resolved' && status !== 'missing' && status !== 'ambiguous') {
    return {
      status: 'unavailable',
      message: 'Reference could not be verified.',
    };
  }

  const nestedTarget =
    root.target ?? root.entry ?? root.match ?? root.reference;
  const target = parseTarget(nestedTarget, root);
  const candidates = Array.isArray(root.candidates)
    ? root.candidates
        .map((candidate) => parseTarget(candidate))
        .filter(
          (candidate): candidate is StudyReferenceTarget =>
            candidate !== undefined,
        )
    : undefined;

  return {
    status,
    target: status === 'resolved' ? target : undefined,
    candidates: status === 'ambiguous' ? candidates : undefined,
    message: firstString([root], 'message', 'detail'),
  };
}

export function queryTagFromLiteral(literalTag: string): string {
  const trimmed = literalTag.trim();
  return trimmed.startsWith('@') ? trimmed.slice(1) : trimmed;
}

/** Resolve a reference without ever inferring a target client-side. */
export async function resolveStudyReference(
  folderId: string,
  tag: string,
): Promise<StudyReferenceResolution> {
  const parameters = new URLSearchParams({ folder_id: folderId, tag });
  const payload = await api<unknown>(
    `/api/references/resolve?${parameters.toString()}`,
  );
  return normalizeStudyReferenceResolution(payload);
}

function kindLabel(kind: string | undefined): string | undefined {
  if (!kind) return undefined;
  return (
    {
      ax: 'Axiom',
      df: 'Definition',
      rk: 'Remark',
      th: 'Theorem',
      pb: 'Problem',
    }[kind] ?? kind
  );
}

export function StudyReference({
  literalTag,
  currentFolderId,
  className,
  onActivate,
  renderPreview,
  resolveReference = resolveStudyReference,
}: StudyReferenceProps) {
  const queryTag = queryTagFromLiteral(literalTag);
  const requestKey = `${currentFolderId}\u0000${queryTag}`;
  const [result, setResult] = useState<{
    requestKey: string;
    resolution: StudyReferenceResolution;
  } | null>(null);
  const resolution =
    result?.requestKey === requestKey ? result.resolution : null;

  useEffect(() => {
    let active = true;

    if (!currentFolderId || !queryTag) {
      return () => {
        active = false;
      };
    }

    void resolveReference(currentFolderId, queryTag)
      .then((result) => {
        if (active) setResult({ requestKey, resolution: result });
      })
      .catch(() => {
        if (active) {
          setResult({
            requestKey,
            resolution: {
              status: 'unavailable',
              message: 'Reference could not be verified.',
            },
          });
        }
      });

    return () => {
      active = false;
    };
  }, [currentFolderId, queryTag, requestKey, resolveReference]);

  const displayedResolution =
    currentFolderId && queryTag
      ? resolution
      : ({
          status: 'unavailable',
          message: 'Reference is incomplete.',
        } as const);

  if (displayedResolution?.status === 'ambiguous') {
    const candidates = displayedResolution.candidates || [];
    return (
      <Popover>
        <PopoverTrigger
          openOnHover
          delay={180}
          closeDelay={180}
          className={cn(
            'inline cursor-help border-0 bg-transparent p-0 font-[inherit] underline decoration-amber/80 decoration-dotted underline-offset-[3px] focus-visible:rounded-sm focus-visible:outline-2 focus-visible:outline-offset-2',
            className,
          )}
          aria-label={`${literalTag}: ambiguous reference; choose an exact tag`}
          data-study-reference-status="ambiguous"
        >
          {literalTag}
        </PopoverTrigger>
        <PopoverContent align="start" side="top" className="reference-ambiguity-popover">
          <PopoverHeader>
            <PopoverTitle>Choose an exact reference</PopoverTitle>
            <PopoverDescription>
              More than one item matches here. Replace {literalTag} with one of these canonical tags.
            </PopoverDescription>
          </PopoverHeader>
          <div className="reference-ambiguity-list">
            {candidates.map((candidate) => {
              const content = <>
                <strong>{candidate.title || candidate.canonicalTag}</strong>
                {candidate.folderNamespace && <small>{candidate.folderNamespace}</small>}
                <code>@{candidate.canonicalTag}</code>
              </>;
              return onActivate ? (
                <button key={`${candidate.entryId}:${candidate.variantId}`} type="button" onClick={() => onActivate(candidate)}>{content}</button>
              ) : (
                <div key={`${candidate.entryId}:${candidate.variantId}`}>{content}</div>
              );
            })}
          </div>
        </PopoverContent>
      </Popover>
    );
  }

  if (displayedResolution?.status !== 'resolved') {
    const status = displayedResolution?.status ?? 'loading';
    const description =
      status === 'missing'
        ? 'Missing reference'
        : status === 'unavailable'
          ? 'Unverified reference'
          : 'Checking reference';

    return (
      <span
        className={cn(
          'rounded-sm underline decoration-dotted underline-offset-[3px]',
          status === 'missing' && 'decoration-destructive/70',
          (status === 'loading' || status === 'unavailable') &&
            'decoration-muted-foreground/60',
          className,
        )}
        data-study-reference-status={status}
        aria-label={`${literalTag} (${description.toLowerCase()})`}
        title={displayedResolution?.message ?? description}
      >
        {literalTag}
      </span>
    );
  }

  const target = displayedResolution.target ?? {};
  const label = kindLabel(target.kind);
  const preview = target.preview;
  const displayText = referenceDisplayText(literalTag, target.title);

  return (
    <Popover>
      <PopoverTrigger
        openOnHover
        delay={180}
        closeDelay={180}
        className={cn(
          'inline cursor-pointer border-0 bg-transparent p-0 font-[inherit] text-primary underline decoration-dotted underline-offset-[3px] focus-visible:rounded-sm focus-visible:outline-2 focus-visible:outline-offset-2',
          className,
        )}
        aria-label={`Preview reference ${displayText}${displayText !== literalTag ? ` (${literalTag})` : ''}`}
        data-study-reference-status="resolved"
      >
        {displayText}
      </PopoverTrigger>
      <PopoverContent
        align="start"
        side="top"
        className="reference-preview-popover"
      >
        <PopoverHeader>
          {label && (
            <span className="text-[0.68rem] font-bold uppercase tracking-[0.08em] text-muted-foreground">
              {label}
            </span>
          )}
          <PopoverTitle className="font-semibold leading-snug">
            {displayText}
          </PopoverTitle>
          {target.canonicalTag && target.canonicalTag !== target.title && (
            <PopoverDescription className="break-all font-mono text-[0.7rem]">
              {target.canonicalTag}
            </PopoverDescription>
          )}
        </PopoverHeader>
        <div className="reference-preview-content">
          {target.header && renderPreview?.(target.header, target)}
          {preview && renderPreview?.(preview, target)}
          {target.header && !renderPreview && <p>{target.header}</p>}
          {preview && !renderPreview && <p>{preview}</p>}
        </div>
        {!preview && !target.title && (
          <p className="m-0 text-sm text-muted-foreground">
            Resolved reference
          </p>
        )}
        {onActivate && (
          <button
            type="button"
            className="self-start rounded-md border border-border bg-secondary px-2.5 py-1.5 text-xs font-semibold text-secondary-foreground hover:bg-accent focus-visible:outline-2 focus-visible:outline-offset-2"
            onClick={() => onActivate(target)}
          >
            Open entry
          </button>
        )}
      </PopoverContent>
    </Popover>
  );
}

export interface StudyReferenceMarkdownSpanProps extends Omit<
  React.ComponentPropsWithoutRef<'span'>,
  'children'
> {
  children?: React.ReactNode;
  node?: unknown;
  currentFolderId: string;
  onActivate?: (target: StudyReferenceTarget) => void;
  resolveReference?: (
    folderId: string,
    tag: string,
  ) => Promise<StudyReferenceResolution>;
  renderPreview?: (content: string, target: StudyReferenceTarget) => ReactNode;
  'data-study-reference'?: string;
}

/** Adapter for ReactMarkdown's `components.span` renderer. */
export function StudyReferenceMarkdownSpan({
  children,
  node: _node,
  currentFolderId,
  onActivate,
  resolveReference,
  renderPreview,
  'data-study-reference': literalTag,
  ...spanProps
}: StudyReferenceMarkdownSpanProps) {
  if (!literalTag) return <span {...spanProps}>{children}</span>;

  return (
    <StudyReference
      literalTag={literalTag}
      currentFolderId={currentFolderId}
      className={spanProps.className}
      onActivate={onActivate}
      resolveReference={resolveReference}
      renderPreview={renderPreview}
    />
  );
}
