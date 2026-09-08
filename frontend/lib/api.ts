let csrfToken = '';
let libraryReadVersion = 0;
const libraryReadListeners = new Set<() => void>();
let libraryReadBatchDepth = 0;
let libraryReadsPending = false;

export function subscribeLibraryReads(listener: () => void) {
  libraryReadListeners.add(listener);
  return () => { libraryReadListeners.delete(listener); };
}

export function getLibraryReadVersion() { return libraryReadVersion; }
export function getServerLibraryReadVersion() { return 0; }

/** Recheck mounted references after a successful content or namespace change. */
export function invalidateLibraryReads() {
  if (libraryReadBatchDepth > 0) {
    libraryReadsPending = true;
    return;
  }
  libraryReadVersion += 1;
  libraryReadListeners.forEach((listener) => listener());
}

/** Refresh readers once after related writes settle, including partially successful saves. */
export async function batchLibraryWrites<T>(write: () => Promise<T>): Promise<T> {
  libraryReadBatchDepth += 1;
  try {
    return await write();
  } finally {
    libraryReadBatchDepth -= 1;
    if (libraryReadBatchDepth === 0 && libraryReadsPending) {
      libraryReadsPending = false;
      invalidateLibraryReads();
    }
  }
}

export function changesLibraryReads(path: string, init: RequestInit): boolean {
  const method = (init.method || 'GET').toUpperCase();
  if (method === 'GET' || method === 'HEAD') return false;
  const route = path.split('?')[0];
  if (route === '/api/git/pull') return true;
  if (!/^\/api\/(?:entries|folders|items|macros)(?:\/|$)/.test(route)) return false;
  if (method === 'PATCH' && /^\/api\/folders\/[^/]+$/.test(route) && typeof init.body === 'string') {
    try {
      const body = JSON.parse(init.body) as Record<string, unknown>;
      if (Object.keys(body).length === 1 && typeof body.review_enabled === 'boolean') return false;
    } catch { /* An invalid body cannot reach a successful mutation response. */ }
  }
  return true;
}

export function setCsrfToken(value: string | null | undefined) {
  csrfToken = value || '';
}

async function parseError(response: Response): Promise<Error> {
  try {
    const body = (await response.json()) as { detail?: string };
    return new Error(body.detail || `${response.status} ${response.statusText}`);
  } catch {
    return new Error(`${response.status} ${response.statusText}`);
  }
}

export async function api<T>(path: string, init: RequestInit = {}): Promise<T> {
  const method = (init.method || 'GET').toUpperCase();
  const headers = new Headers(init.headers);
  if (method !== 'GET' && method !== 'HEAD' && csrfToken) {
    headers.set('x-study-csrf', csrfToken);
  }
  if (init.body && !(init.body instanceof FormData) && !headers.has('content-type')) {
    headers.set('content-type', 'application/json');
  }
  const response = await fetch(path, { ...init, headers, credentials: 'same-origin' });
  if (!response.ok) throw await parseError(response);
  const result = (await response.json()) as T;
  if (changesLibraryReads(path, init)) invalidateLibraryReads();
  return result;
}

export async function apiFile(path: string, init: RequestInit): Promise<{ blob: Blob; filename: string }> {
  const headers = new Headers(init.headers);
  if (csrfToken) headers.set('x-study-csrf', csrfToken);
  if (init.body && !(init.body instanceof FormData)) headers.set('content-type', 'application/json');
  const response = await fetch(path, { ...init, headers, credentials: 'same-origin' });
  if (!response.ok) throw await parseError(response);
  const disposition = response.headers.get('content-disposition') || '';
  const match = disposition.match(/filename="?([^";]+)"?/i);
  return { blob: await response.blob(), filename: match?.[1] || 'study-export.pdf' };
}

export function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
