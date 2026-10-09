'use client';

import { memo, useEffect, useState } from 'react';
import { MathMarkdown } from '@/components/MathMarkdown';

const PREVIEW_IDLE_MS = 500;

/** Editing updates the draft immediately; only the rendered snapshot waits for idle. */
function EditorPreviewComponent({ header, content, folderId }: {
  header: string;
  content: string;
  folderId: string;
}) {
  const [rendered, setRendered] = useState(() => ({ header, content }));
  const pending = header !== rendered.header || content !== rendered.content;

  useEffect(() => {
    if (!pending) return;
    const timer = window.setTimeout(() => setRendered({ header, content }), PREVIEW_IDLE_MS);
    return () => window.clearTimeout(timer);
  }, [header, content, pending]);

  return <div className="editor-preview" aria-busy={pending}>
    {rendered.header && <MathMarkdown content={rendered.header}
      className="content-header editor-header-preview" folderId={folderId} />}
    <MathMarkdown content={rendered.content} folderId={folderId} />
  </div>;
}

export const EditorPreview = memo(EditorPreviewComponent);
