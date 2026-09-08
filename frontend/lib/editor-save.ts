import type { EntryDetail, EntryKind } from './types';

interface EditorFields {
  title: string;
  tag: string;
  kind: EntryKind;
  header: string;
}

/** Persist only changed values; mutation responses already contain the saved entry. */
export async function saveEditorChanges(
  working: EntryDetail,
  fields: EditorFields,
  drafts: Record<string, string>,
  request: (path: string, init?: RequestInit) => Promise<EntryDetail>,
  retryAll = false,
): Promise<EntryDetail | null> {
  const updates = Object.fromEntries(
    Object.entries(fields).filter(([key, value]) => retryAll || value !== working[key as keyof EditorFields]),
  );
  const changedVariants = [...working.formulations, ...working.supplements].filter(
    (variant) => retryAll || (drafts[variant.id] ?? variant.content ?? '') !== (variant.content ?? ''),
  );
  let saved: EntryDetail | null = null;
  if (Object.keys(updates).length) {
    saved = await request(`/api/entries/${working.id}`, {
      method: 'PATCH', body: JSON.stringify(updates),
    });
  }
  if (!changedVariants.length) return saved;

  const writes = await Promise.allSettled(changedVariants.map((variant) => request(
    `/api/entries/${working.id}/content/${variant.id}`,
    { method: 'PUT', body: JSON.stringify({ content: drafts[variant.id] ?? variant.content ?? '' }) },
  )));
  // A failed write must not unlock a retry while another write is still in flight.
  const failed = writes.find((result) => result.status === 'rejected');
  if (failed?.status === 'rejected') throw failed.reason;
  if (writes.length === 1 && writes[0].status === 'fulfilled') return writes[0].value;
  return request(`/api/entries/${working.id}`);
}
