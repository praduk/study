let csrfToken = '';

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
  return (await response.json()) as T;
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
