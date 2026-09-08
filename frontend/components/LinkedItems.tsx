'use client';

import { useCallback, useEffect, useRef, useState, useSyncExternalStore } from 'react';
import { Link2, LoaderCircle } from 'lucide-react';

import { Button } from '@/components/ui/button';
import { api, getLibraryReadVersion, getServerLibraryReadVersion, subscribeLibraryReads } from '@/lib/api';
import { appendLinkedItems, linkedItemPath, type LinkedItemsPage } from '@/lib/linked-items';

export function LinkedItems({ entryId, onOpenEntry }: {
  entryId: string;
  onOpenEntry: (entryId: string, variantId?: string) => void;
}) {
  const version = useSyncExternalStore(subscribeLibraryReads, getLibraryReadVersion, getServerLibraryReadVersion);
  // Changing the key also cancels a pending continuation and removes the old entry's list immediately.
  return <LinkedItemsList key={`${entryId}:${version}`} entryId={entryId} onOpenEntry={onOpenEntry} />;
}

function LinkedItemsList({ entryId, onOpenEntry }: {
  entryId: string;
  onOpenEntry: (entryId: string, variantId?: string) => void;
}) {
  const [page, setPage] = useState<LinkedItemsPage | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [refreshed, setRefreshed] = useState(false);
  const currentRequest = useRef<AbortController | null>(null);

  const load = useCallback(async (offset: number, current: LinkedItemsPage | null): Promise<void> => {
    currentRequest.current?.abort();
    const controller = new AbortController();
    currentRequest.current = controller;
    try {
      const query = new URLSearchParams({ offset: String(offset), limit: '40' });
      const result = await api<LinkedItemsPage>(`/api/entries/${entryId}/linked-items?${query}`, { signal: controller.signal });
      if (controller.signal.aborted) return;
      let merged = appendLinkedItems(current, result);
      if (!merged) {
        // A content edit can change both ordering and counts between requests.
        setPage(null);
        setRefreshed(true);
        merged = await api<LinkedItemsPage>(`/api/entries/${entryId}/linked-items?offset=0&limit=40`, { signal: controller.signal });
        if (controller.signal.aborted) return;
      }
      setPage(merged);
    } catch (reason) {
      if (!controller.signal.aborted) setError(reason instanceof Error ? reason.message : 'Linked items could not be loaded.');
    } finally {
      if (currentRequest.current === controller && !controller.signal.aborted) setLoading(false);
    }
  }, [entryId]);

  function startLoad(offset: number, current: LinkedItemsPage | null) {
    setLoading(true);
    setError('');
    void load(offset, current);
  }

  useEffect(() => {
    const controller = new AbortController();
    currentRequest.current = controller;
    api<LinkedItemsPage>(`/api/entries/${entryId}/linked-items?offset=0&limit=40`, { signal: controller.signal })
      .then((result) => { if (!controller.signal.aborted) setPage(result); })
      .catch((reason: Error) => { if (!controller.signal.aborted) setError(reason.message); })
      .finally(() => { if (!controller.signal.aborted) setLoading(false); });
    return () => currentRequest.current?.abort();
  }, [entryId]);

  return <section className="linked-items" aria-labelledby={`linked-items-${entryId}`} aria-busy={loading}>
    <div className="linked-items-heading">
      <h2 id={`linked-items-${entryId}`}><Link2 aria-hidden="true" /> Linked items {page && <span className="linked-items-count">{page.total}</span>}</h2>
      <p>Items that use a tag for this entry or one of its formulations, proofs, or solutions.</p>
    </div>
    {page && page.total === 0 && <p className="linked-items-status">No items reference this entry yet.</p>}
    {!!page?.items.length && <ul className="linked-items-list">{page.items.map((item) => <li key={item.entry_id}>
      <a href={linkedItemPath(item)} onClick={(event) => {
        if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
        event.preventDefault();
        onOpenEntry(item.entry_id, item.variant_id ?? undefined);
      }}>
        <span className={`type-chip type-${item.kind}`} aria-hidden="true">{item.kind}</span>
        <span><strong>{item.title}</strong><small>{item.folder_namespace.split(':').join(' / ')} · {item.source === 'header' ? 'Header' : item.label}{item.reference_count > 1 ? ` · ${item.reference_count} locations` : ''}</small></span>
      </a>
    </li>)}</ul>}
    <output className="linked-items-status" aria-live="polite">
      {loading && <span><LoaderCircle className="spin" aria-hidden="true" /> Loading linked items…</span>}
      {!loading && refreshed && <p>The library changed. The list has been refreshed.</p>}
      {!loading && page && page.next_offset !== null && <span>Showing {page.items.length} of {page.total} items.</span>}
    </output>
    {error && <div className="linked-items-error" role="alert"><p>{error}</p><Button variant="outline" size="sm" onClick={() => startLoad(page?.next_offset ?? 0, page)}>Retry</Button></div>}
    {page && page.next_offset !== null && !error && <Button variant="outline" size="sm" disabled={loading} onClick={() => startLoad(page.next_offset!, page)}>Show more linked items</Button>}
  </section>;
}
