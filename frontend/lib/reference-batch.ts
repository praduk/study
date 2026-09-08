interface PendingReference<T> {
  tag: string;
  promise: Promise<T>;
  resolve: (value: T) => void;
  reject: (reason: unknown) => void;
}

export function referenceBatchPath(folderId: string, tags: string[]) {
  const parameters = new URLSearchParams({ folder_id: folderId });
  tags.forEach((tag) => parameters.append('tag', tag));
  return `/api/references/resolve-batch?${parameters}`;
}

/** Coalesce one render's lookups, retaining only requests that are still in flight. */
export function createReferenceBatcher<T>(
  request: (folderId: string, tags: string[]) => Promise<Map<string, T>>,
  limits = { tags: 100, urlLength: 6000 },
) {
  const pending = new Map<string, PendingReference<T>>();
  const queued = new Map<string, { folderId: string; requests: PendingReference<T>[] }>();
  let scheduled = false;

  function flush() {
    scheduled = false;
    const groups = [...queued.entries()];
    queued.clear();
    for (const [scope, group] of groups) {
      const chunks: PendingReference<T>[][] = [];
      let chunk: PendingReference<T>[] = [];
      for (const item of group.requests) {
        const tags = [...chunk.map((candidate) => candidate.tag), item.tag];
        if (chunk.length && (tags.length > limits.tags || referenceBatchPath(group.folderId, tags).length > limits.urlLength)) {
          chunks.push(chunk);
          chunk = [];
        }
        chunk.push(item);
      }
      if (chunk.length) chunks.push(chunk);
      for (const requests of chunks) {
        void Promise.resolve().then(() => request(group.folderId, requests.map((item) => item.tag)))
          .then((results) => {
            for (const item of requests) {
              pending.delete(`${scope}\u0000${item.tag}`);
              if (results.has(item.tag)) item.resolve(results.get(item.tag)!);
              else item.reject(new Error('Reference was absent from the batch response.'));
            }
          }, (reason: unknown) => {
            for (const item of requests) pending.delete(`${scope}\u0000${item.tag}`);
            requests.forEach((item) => item.reject(reason));
          });
      }
    }
  }

  return (folderId: string, tag: string, version = 0): Promise<T> => {
    const scope = `${version}\u0000${folderId}`;
    const key = `${scope}\u0000${tag}`;
    const existing = pending.get(key);
    if (existing) return existing.promise;
    let resolve!: (value: T) => void;
    let reject!: (reason: unknown) => void;
    const promise = new Promise<T>((onResolve, onReject) => { resolve = onResolve; reject = onReject; });
    const item = { tag, promise, resolve, reject };
    pending.set(key, item);
    const group = queued.get(scope) ?? { folderId, requests: [] };
    group.requests.push(item);
    queued.set(scope, group);
    if (!scheduled) { scheduled = true; queueMicrotask(flush); }
    return promise;
  };
}
