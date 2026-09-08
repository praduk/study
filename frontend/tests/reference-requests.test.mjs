import assert from 'node:assert/strict';
import test from 'node:test';

import { api, batchLibraryWrites, changesLibraryReads, getLibraryReadVersion, subscribeLibraryReads } from '../lib/api.ts';
import { appendLinkedItems, linkedItemPath } from '../lib/linked-items.ts';
import { createReferenceBatcher, referenceBatchPath } from '../lib/reference-batch.ts';

test('a render batches references by folder and deduplicates identical in-flight requests', async () => {
  const calls = [];
  const resolve = createReferenceBatcher(async (folder, tags) => {
    calls.push({ folder, tags });
    return new Map(tags.map((tag) => [tag, `${folder}:${tag}`]));
  });
  const a = resolve('math', 'group');
  assert.equal(resolve('math', 'group'), a);
  const results = await Promise.all([a, resolve('math', 'ring'), resolve('physics', 'group')]);
  assert.deepEqual(results, ['math:group', 'math:ring', 'physics:group']);
  assert.deepEqual(calls, [{ folder: 'math', tags: ['group', 'ring'] }, { folder: 'physics', tags: ['group'] }]);
  await resolve('math', 'group');
  assert.equal(calls.length, 3, 'completed results are not cached across reads');
});

test('reference batches bound tag count and encoded URL length', async () => {
  const calls = [];
  const resolve = createReferenceBatcher(async (folder, tags) => {
    calls.push({ folder, tags });
    return new Map(tags.map((tag) => [tag, tag]));
  }, { tags: 2, urlLength: 90 });
  await Promise.all(['a', 'b', 'c', 'x'.repeat(100)].map((tag) => resolve('folder', tag)));
  assert.ok(calls.every(({ tags }) => tags.length <= 2));
  assert.ok(calls.every(({ folder, tags }) => tags.length === 1 || referenceBatchPath(folder, tags).length <= 90));
  assert.deepEqual(calls.flatMap(({ tags }) => tags), ['a', 'b', 'c', 'x'.repeat(100)]);
});

test('a changed library cannot reuse an old in-flight reference result', async () => {
  const calls = [];
  const resolve = createReferenceBatcher(async (_folder, tags) => {
    calls.push(tags);
    return new Map(tags.map((tag) => [tag, tag]));
  });
  const old = resolve('math', 'group', 0);
  const fresh = resolve('math', 'group', 1);
  assert.notEqual(old, fresh);
  await Promise.all([old, fresh]);
  assert.equal(calls.length, 2);
});

test('batch errors and incomplete responses reject affected callers and remain retryable', async () => {
  let attempt = 0;
  const resolve = createReferenceBatcher(async (_folder, tags) => {
    attempt += 1;
    if (attempt === 1) throw new Error('offline');
    return new Map(tags.filter((tag) => tag !== 'missing-row').map((tag) => [tag, tag]));
  });
  await assert.rejects(resolve('math', 'group'), /offline/);
  assert.equal(await resolve('math', 'group'), 'group');
  await assert.rejects(resolve('math', 'missing-row'), /absent/);
});

test('only successful content-changing API calls refresh mounted library reads', async () => {
  const before = getLibraryReadVersion();
  let updates = 0;
  const unsubscribe = subscribeLibraryReads(() => { updates += 1; });
  const originalFetch = globalThis.fetch;
  globalThis.fetch = async () => new Response('{}', { status: 200, headers: { 'Content-Type': 'application/json' } });
  try {
    await api('/api/entries/one/content/two', { method: 'PUT', body: '{}' });
    assert.equal(getLibraryReadVersion(), before + 1);
    await api('/api/folders/one', { method: 'PATCH', body: '{"review_enabled":true}' });
    await api('/api/review/grade', { method: 'POST', body: '{}' });
    await api('/api/entries/one');
    assert.equal(updates, 1);
    globalThis.fetch = async () => new Response('{"detail":"failed"}', { status: 400 });
    await assert.rejects(api('/api/entries/one', { method: 'DELETE' }), /failed/);
    assert.equal(updates, 1);
  } finally { globalThis.fetch = originalFetch; unsubscribe(); }
  assert.equal(changesLibraryReads('/api/git/pull', { method: 'POST' }), true);
  assert.equal(changesLibraryReads('/api/folders/one', { method: 'PATCH', body: '{"slug":"new"}' }), true);
});

test('linked-item pagination keeps authored order and rejects a changed snapshot', () => {
  const base = { entry_id: 'target', revision: 'one', total: 3, offset: 0, limit: 2, next_offset: 2, items: [{ entry_id: 'a' }, { entry_id: 'b' }] };
  const next = { ...base, offset: 2, next_offset: null, items: [{ entry_id: 'c' }] };
  assert.deepEqual(appendLinkedItems(base, next).items.map((item) => item.entry_id), ['a', 'b', 'c']);
  assert.equal(appendLinkedItems(base, { ...next, revision: 'two' }), null);
  assert.equal(appendLinkedItems(base, { ...next, entry_id: 'other' }), null);
  assert.equal(appendLinkedItems(base, { ...next, offset: 1 }), null);
  assert.equal(appendLinkedItems(base, { ...next, offset: 0, revision: 'two' }).revision, 'two');
  assert.equal(linkedItemPath({ canonical_tag: 'math:algebra:th:lagrange:pf:action' }), '/library/math/algebra/th/lagrange/pf/action');
});

test('related writes refresh readers once, after completion or partial failure', async () => {
  const originalFetch = globalThis.fetch;
  const before = getLibraryReadVersion();
  let updates = 0;
  const unsubscribe = subscribeLibraryReads(() => { updates += 1; });
  globalThis.fetch = async (path) => path.endsWith('/failed')
    ? new Response('{"detail":"failed"}', { status: 400 })
    : new Response('{}', { status: 200 });
  try {
    await batchLibraryWrites(async () => {
      await api('/api/entries/one', { method: 'PATCH', body: '{}' });
      await batchLibraryWrites(async () => {
        await api('/api/entries/one/content/two', { method: 'PUT', body: '{}' });
      });
      assert.equal(updates, 0, 'nested work must not expose an intermediate library');
    });
    assert.equal(updates, 1);
    assert.equal(getLibraryReadVersion(), before + 1);
    await assert.rejects(batchLibraryWrites(async () => {
      await api('/api/entries/one', { method: 'PATCH', body: '{}' });
      await api('/api/entries/failed', { method: 'PATCH', body: '{}' });
    }), /failed/);
    assert.equal(updates, 2, 'successful writes before a failure still invalidate readers');
    await assert.rejects(batchLibraryWrites(async () => {
      await api('/api/entries/failed', { method: 'PATCH', body: '{}' });
    }), /failed/);
    assert.equal(updates, 2, 'a failed-only batch changes no successful-read state');
  } finally { globalThis.fetch = originalFetch; unsubscribe(); }
});
