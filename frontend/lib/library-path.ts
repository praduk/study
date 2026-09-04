import type { EntrySummary, Folder, Variant } from '@/lib/types';

const LIBRARY_PREFIX = '/library/';
const PATH_SEGMENT = /^[a-z][a-z0-9-]*$/;

export type LibraryPathResolution =
  | { kind: 'root' }
  | {
      kind: 'entry';
      entry: EntrySummary;
      variantId: string | null;
      canonicalPath: string;
    }
  | { kind: 'missing' };

function formulationCanonicalTag(entry: EntrySummary, formulation: Omit<Variant, 'content'>) {
  return formulation.main || !formulation.subtag
    ? entry.canonical_tag
    : `${entry.canonical_tag}:${formulation.subtag}`;
}

function supplementCanonicalTag(entry: EntrySummary, supplement: Omit<Variant, 'content'>) {
  if (!supplement.kind) return '';
  const base = `${entry.canonical_tag}:${supplement.kind}`;
  return supplement.main || !supplement.subtag ? base : `${base}:${supplement.subtag}`;
}

function variantCanonicalTag(entry: EntrySummary, variantId: string | null) {
  if (!variantId) return entry.canonical_tag;
  const formulation = entry.formulations.find((item) => item.id === variantId);
  if (formulation) return formulationCanonicalTag(entry, formulation);
  const supplement = entry.supplements.find((item) => item.id === variantId);
  return supplement ? supplementCanonicalTag(entry, supplement) : entry.canonical_tag;
}

function canonicalPath(canonicalTag: string) {
  return `${LIBRARY_PREFIX}${canonicalTag.split(':').map(encodeURIComponent).join('/')}`;
}

export function libraryPathForEntry(entry: EntrySummary, variantId: string | null = null) {
  return canonicalPath(variantCanonicalTag(entry, variantId));
}

export function resolveLibraryPath(
  pathname: string,
  entries: EntrySummary[],
): LibraryPathResolution {
  if (pathname === '' || pathname === '/') return { kind: 'root' };
  if (!pathname.startsWith(LIBRARY_PREFIX)) return { kind: 'missing' };

  const relative = pathname.slice(LIBRARY_PREFIX.length).replace(/\/$/, '');
  if (!relative) return { kind: 'missing' };
  let segments: string[];
  try {
    segments = relative.split('/').map(decodeURIComponent);
  } catch {
    return { kind: 'missing' };
  }
  if (segments.some((segment) => !PATH_SEGMENT.test(segment))) return { kind: 'missing' };
  const requestedTag = segments.join(':');

  for (const entry of entries) {
    if (entry.canonical_tag === requestedTag) {
      return {
        kind: 'entry',
        entry,
        variantId: null,
        canonicalPath: libraryPathForEntry(entry),
      };
    }
    for (const formulation of entry.formulations) {
      if (!formulation.main && formulationCanonicalTag(entry, formulation) === requestedTag) {
        return {
          kind: 'entry',
          entry,
          variantId: formulation.id,
          canonicalPath: libraryPathForEntry(entry, formulation.id),
        };
      }
    }
    for (const supplement of entry.supplements) {
      if (supplementCanonicalTag(entry, supplement) === requestedTag) {
        return {
          kind: 'entry',
          entry,
          variantId: supplement.id,
          canonicalPath: libraryPathForEntry(entry, supplement.id),
        };
      }
    }
  }
  return { kind: 'missing' };
}

export function folderPathIds(folderId: string, folders: Folder[]) {
  const byId = new Map(folders.map((folder) => [folder.id, folder]));
  const result = new Set<string>();
  let current: string | null = folderId;
  while (current && !result.has(current)) {
    result.add(current);
    current = byId.get(current)?.parent_id || null;
  }
  return result;
}
