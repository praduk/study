import assert from 'node:assert/strict';
import test from 'node:test';

import { saveEditorChanges } from '../lib/editor-save.ts';

const entry = {
  id: 'entry', title: 'Example', tag: 'example', kind: 'th', header: 'Scope',
  formulations: [{ id: 'main', content: 'Statement\n' }],
  supplements: [{ id: 'proof', content: 'Proof\n' }],
};
const fields = { title: entry.title, tag: entry.tag, kind: entry.kind, header: entry.header };
const drafts = { main: 'Statement\n', proof: 'Proof\n' };

test('an unchanged save sends no requests and does not reload the library', async () => {
  const saved = await saveEditorChanges(entry, fields, drafts, async () => {
    assert.fail('unchanged entry must not send a request');
  });
  assert.equal(saved, null);
});

test('editing one body skips unchanged metadata, proof, and redundant entry reads', async () => {
  const calls = [];
  const response = { ...entry, formulations: [{ id: 'main', content: 'Revised\n' }] };
  const saved = await saveEditorChanges(entry, fields, { ...drafts, main: 'Revised' }, async (path, init) => {
    calls.push({ path, ...init });
    return response;
  });
  assert.equal(saved, response, 'return the authoritative normalized server response');
  assert.deepEqual(calls, [{ path: '/api/entries/entry/content/main', method: 'PUT', body: '{"content":"Revised"}' }]);
  assert.equal(await saveEditorChanges(saved, fields, { ...drafts, main: saved.formulations[0].content }, async () => {
    assert.fail('saving the reconciled draft again must be a no-op');
  }), null);
});

test('metadata-only edits omit unchanged kind and content', async () => {
  const calls = [];
  const response = { ...entry, title: 'Renamed' };
  assert.equal(await saveEditorChanges(entry, { ...fields, title: 'Renamed' }, drafts, async (path, init) => {
    calls.push({ path, ...init });
    return response;
  }), response);
  assert.deepEqual(calls, [{ path: '/api/entries/entry', method: 'PATCH', body: '{"title":"Renamed"}' }]);
});

test('clearing a body is an intentional write and missing drafts leave variants alone', async () => {
  const calls = [];
  await saveEditorChanges(entry, fields, { main: '' }, async (path, init) => {
    calls.push({ path, ...init });
    return entry;
  });
  assert.deepEqual(calls, [{ path: '/api/entries/entry/content/main', method: 'PUT', body: '{"content":""}' }]);
});

test('multiple edited variants settle before the final authoritative read', async () => {
  const calls = [];
  let releaseProof;
  const held = new Promise((resolve) => { releaseProof = resolve; });
  const saving = saveEditorChanges(entry, { ...fields, header: 'New scope' }, { main: 'New', proof: 'New proof' }, async (path, init) => {
    calls.push({ path, method: init?.method || 'GET' });
    if (path.endsWith('/proof')) await held;
    return entry;
  });
  await new Promise((resolve) => setImmediate(resolve));
  assert.deepEqual(calls.map((call) => call.method), ['PATCH', 'PUT', 'PUT']);
  releaseProof();
  await saving;
  assert.deepEqual(calls.map((call) => call.method), ['PATCH', 'PUT', 'PUT', 'GET']);
});

test('a failed variant does not finish the save while another variant is pending', async () => {
  let releaseProof;
  const held = new Promise((resolve) => { releaseProof = resolve; });
  let finished = false;
  const saving = saveEditorChanges(entry, fields, { main: 'New', proof: 'New proof' }, async (path) => {
    if (path.endsWith('/main')) throw new Error('write failed');
    if (path.endsWith('/proof')) { await held; return entry; }
    assert.fail('failed saves must not report a refreshed successful entry');
  }).finally(() => { finished = true; });
  const rejected = assert.rejects(saving, /write failed/);
  await new Promise((resolve) => setImmediate(resolve));
  assert.equal(finished, false);
  releaseProof();
  await rejected;
});

test('retrying after a partial save writes reverted fields as well as changed bodies', async () => {
  const calls = [];
  // The original baseline still says Example, but a failed earlier save already
  // renamed the stored entry. The user has now reverted the title to Example.
  await saveEditorChanges(entry, fields, { ...drafts, main: 'Retry body' }, async (path, init) => {
    calls.push({ path, ...init });
    return entry;
  }, true);
  assert.equal(calls[0].method, 'PATCH');
  assert.equal(JSON.parse(calls[0].body).title, 'Example');
  assert.deepEqual(calls.filter((call) => call.method === 'PUT').map((call) => call.path), [
    '/api/entries/entry/content/main', '/api/entries/entry/content/proof',
  ]);
});
