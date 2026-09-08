import type { EntryKind } from '@/lib/types';

export interface LinkedItem {
  entry_id: string;
  title: string;
  kind: EntryKind;
  canonical_tag: string;
  folder_id: string;
  folder_namespace: string;
  variant_id: string | null;
  source: 'header' | 'formulation' | 'supplement';
  label: string;
  reference_count: number;
}

export interface LinkedItemsPage {
  entry_id: string;
  revision: string;
  total: number;
  offset: number;
  limit: number;
  next_offset: number | null;
  items: LinkedItem[];
}

export function linkedItemPath(item: LinkedItem) {
  return `/library/${item.canonical_tag.split(':').map(encodeURIComponent).join('/')}`;
}

/** Reject continuation pages from a replaced index, so entries cannot be skipped or repeated. */
export function appendLinkedItems(current: LinkedItemsPage | null, page: LinkedItemsPage): LinkedItemsPage | null {
  if (page.offset === 0) return page;
  if (!current || page.entry_id !== current.entry_id || page.revision !== current.revision || page.offset !== current.next_offset) return null;
  return { ...page, offset: 0, items: [...current.items, ...page.items] };
}
