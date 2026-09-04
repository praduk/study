'use client';

import { memo, useEffect, useMemo, useRef, useSyncExternalStore } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';

import { CommutativeDiagramView } from '@/components/CommutativeDiagramView';
import { LightnessImage } from '@/components/LightnessImage';
import {
  StudyReferenceMarkdownSpan,
  type StudyReferenceTarget,
} from '@/components/StudyReference';
import { mathJaxMarkdownHandlers, normalizeMathJaxDelimiters, remarkStudyMath } from '@/lib/markdown-math';
import { typesetWithMathJax } from '@/lib/mathjax';
import {
  remarkStudyDiagrams,
  STUDY_COMMUTATIVE_ATTRIBUTE,
  STUDY_COMMUTATIVE_WIDTH_ATTRIBUTE,
} from '@/lib/remark-study-diagrams';
import { remarkStudyReferences } from '@/lib/remark-study-references';

type OpenReference = (entryId: string, variantId?: string) => void;

function subscribeTheme(onChange: () => void) {
  const observer = new MutationObserver(onChange);
  observer.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] });
  return () => observer.disconnect();
}

function getThemeSnapshot() {
  return document.documentElement.classList.contains('dark');
}

interface MarkdownBlockProps {
  content: string;
  className?: string;
  folderId?: string;
  onOpenEntry?: OpenReference;
  interactive?: boolean;
}

function MarkdownBlock({ content, className = '', folderId = '', onOpenEntry, interactive = true }: MarkdownBlockProps) {
  const container = useRef<HTMLDivElement>(null);
  const dark = useSyncExternalStore(subscribeTheme, getThemeSnapshot, () => false);
  const normalizedContent = useMemo(() => normalizeMathJaxDelimiters(content), [content]);
  const remarkPlugins = useMemo(
    () => interactive
      ? [remarkGfm, remarkMath, remarkStudyMath, remarkStudyReferences, remarkStudyDiagrams]
      : [remarkGfm, remarkMath, remarkStudyMath, remarkStudyDiagrams],
    [interactive],
  );
  useEffect(() => {
    const element = container.current;
    if (!element) return;
    void typesetWithMathJax(element).catch(() => undefined);
  }, [content, dark, interactive]);

  return (
    <div ref={container} className={className}>
      <ReactMarkdown
        key={`${dark ? 'dark' : 'light'}:${interactive ? 'interactive' : 'static'}:${normalizedContent}`}
        remarkPlugins={remarkPlugins}
        remarkRehypeOptions={{ handlers: mathJaxMarkdownHandlers }}
        components={{
          a({ children, href, title }) {
            if (!interactive) return <span className="markdown-link-disabled">{children}</span>;
            return <a href={href} title={title}>{children}</a>;
          },
          div({ node: _node, children, ...props }) {
            const diagramProperties = props as typeof props & Record<string, unknown>;
            const id = diagramProperties[STUDY_COMMUTATIVE_ATTRIBUTE];
            if (typeof id === 'string') {
              const requestedWidth = Number(
                diagramProperties[STUDY_COMMUTATIVE_WIDTH_ATTRIBUTE],
              );
              const width = Number.isFinite(requestedWidth)
                ? Math.min(100, Math.max(10, requestedWidth))
                : 76;
              return <CommutativeDiagramView id={id} width={width} />;
            }
            return <div {...props}>{children}</div>;
          },
          img({ src = '', alt = '' }) {
            const source = typeof src === 'string' ? src : '';
            const [path, fragment = ''] = source.split('#');
            const parameters = new URLSearchParams(fragment);
            const width = Number(parameters.get('width') || '76');
            return (
              <LightnessImage
                src={path}
                alt={alt}
                widthPercent={Number.isFinite(width) ? width : 76}
                invertLightness={parameters.get('invert') === 'lightness'}
              />
            );
          },
          span(props) {
            const activate = onOpenEntry
              ? (target: StudyReferenceTarget) =>
                  target.entryId && onOpenEntry(target.entryId, target.variantId)
              : undefined;
            return <StudyReferenceMarkdownSpan
              {...props}
              currentFolderId={folderId}
              onActivate={activate}
              renderPreview={(previewContent, target) => (
                <MathMarkdown
                  content={previewContent}
                  className="reference-preview-markdown"
                  folderId={target.folderId || folderId}
                  interactive={false}
                />
              )}
            />;
          },
        }}
      >
        {normalizedContent}
      </ReactMarkdown>
    </div>
  );
}

interface MathMarkdownProps {
  content: string;
  className?: string;
  folderId?: string;
  onOpenEntry?: OpenReference;
  interactive?: boolean;
}

function MathMarkdownComponent({ content, className = 'markdown-body', folderId = '', onOpenEntry, interactive = true }: MathMarkdownProps) {
  return (
    <div className={className}>
      <MarkdownBlock content={content} folderId={folderId} onOpenEntry={onOpenEntry} interactive={interactive} />
    </div>
  );
}

// MathJax replaces the source delimiters in this subtree with SVG. Keep React from
// reconciling that externally managed DOM when an unrelated parent state change
// (such as dragging the library separator) renders the page again.
export const MathMarkdown = memo(MathMarkdownComponent);
