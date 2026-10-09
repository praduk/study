'use client';

import { useEffect, useRef, useState } from 'react';

export function TikzCdView({ source }: { source: string }) {
  const container = useRef<HTMLDivElement>(null);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(true);
  useEffect(() => {
    const controller = new AbortController();
    const node = container.current;
    if (!node) return;
    void import('@/lib/tikz-renderer').then(async ({ renderTikzCd, prepareTikzSvg }) => {
      if (controller.signal.aborted) return;
      setBusy(true); setError('');
      const svg = await renderTikzCd(source, controller.signal);
      if (!controller.signal.aborted) {
        const prepared = prepareTikzSvg(svg);
        node.replaceChildren(prepared); setBusy(false);
      }
    }).catch((reason: Error) => {
      if (!controller.signal.aborted) { setError(reason.message); setBusy(false); node.replaceChildren(); }
    });
    return () => controller.abort();
  }, [source]);
  return <figure className="tikzcd-view" aria-busy={busy}>
    <div ref={container} className="tikzcd-svg" />
    {busy && <figcaption>Rendering diagram…</figcaption>}
    {error && <div className="form-error" role="alert">{error}<details><summary>TikZ-CD source</summary><pre>{source}</pre></details></div>}
  </figure>;
}
