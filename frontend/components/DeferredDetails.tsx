'use client';

import { useState, type ReactNode } from 'react';

/** Leave collapsed Markdown unmounted until its first expansion. */
export function DeferredDetails({ initiallyOpen = false, className, summary, children }: {
  initiallyOpen?: boolean;
  className?: string;
  summary: ReactNode;
  children: ReactNode;
}) {
  const [opened, setOpened] = useState(initiallyOpen);
  return <details open={initiallyOpen} className={className} onToggle={(event) => {
    if (event.currentTarget.open) setOpened(true);
  }}>
    <summary>{summary}</summary>
    {opened && children}
  </details>;
}
