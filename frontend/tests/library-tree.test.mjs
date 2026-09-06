import assert from 'node:assert/strict';
import test from 'node:test';

import {
  buildLibraryTree,
  hydrateBootstrap,
  updateBootstrapFolder,
} from '../lib/library-tree.ts';

function folder(id, name, order, parentId = null, reviewEnabled = true) {
  return {
    id,
    name,
    slug: id,
    namespace: id,
    parent_id: parentId,
    order,
    review_enabled: reviewEnabled,
  };
}

function entry(id, folderId, title, order) {
  return {
    id,
    folder_id: folderId,
    kind: 'df',
    title,
    tag: id,
    header: '',
    order,
    canonical_tag: `${folderId}:df:${id}`,
    review_modes: ['statement'],
    formulations: [],
    supplements: [],
    assets: [],
  };
}

function compactPayload(folders, entries) {
  return {
    version: 2,
    folders,
    entries,
    macros: {},
    review: {
      due: 0,
      completed_today: 0,
      minutes_today: 0,
      calibration: {
        model: 'test',
        target_grade: 'good-or-easy',
        target_probability: 0.9,
        minimum_observations: 24,
        minimum_delay_hours: 6,
        processed_log_records: 0,
        models: {},
      },
    },
    git: { available: false },
    capabilities: {},
  };
}

test('compact bootstrap hydration reproduces backend authored tree order', () => {
  const folders = [
    folder('stable-second', 'Same', 3),
    folder('child-zulu', 'Zulu', 1, 'root-zulu'),
    folder('root-umlaut', 'Älgebra', 1),
    folder('child-alpha', 'alpha', 1, 'root-zulu'),
    folder('root-zulu', 'Zulu', 1),
    folder('root-emoji', '😀 Emoji', 2),
    folder('root-private-use', '\ue000 Private use', 2),
    folder('stable-first', 'Same', 3),
  ];
  const entries = [
    entry('stable-entry-second', 'root-zulu', 'Same', 3),
    entry('entry-umlaut', 'root-zulu', 'Älgebra', 1),
    entry('entry-zulu', 'root-zulu', 'Zulu', 1),
    entry('stable-entry-first', 'root-zulu', 'Same', 3),
    entry('entry-first', 'root-zulu', 'First', 0),
  ];

  const hydrated = hydrateBootstrap(compactPayload(folders, entries));

  assert.deepEqual(hydrated.tree.map((node) => node.id), [
    'root-zulu',
    'root-umlaut',
    'root-private-use',
    'root-emoji',
    'stable-second',
    'stable-first',
  ]);
  assert.deepEqual(hydrated.tree[0].children.map((node) => node.id), [
    'child-alpha',
    'child-zulu',
  ]);
  assert.deepEqual(hydrated.tree[0].entries.map((item) => item.id), [
    'entry-first',
    'entry-zulu',
    'entry-umlaut',
    'stable-entry-second',
    'stable-entry-first',
  ]);
  assert.strictEqual(hydrated.tree[0].entries[0], entries[4]);
});

test('hydration preserves a full bootstrap tree supplied by the server', () => {
  const folders = [folder('root', 'Root', 0)];
  const entries = [entry('entry', 'root', 'Entry', 0)];
  const tree = buildLibraryTree(folders, entries);
  const hydrated = hydrateBootstrap({ ...compactPayload(folders, entries), tree });

  assert.strictEqual(hydrated.tree, tree);
});

test('folder updates preserve entries and unaffected tree identities', () => {
  const folders = [
    folder('root', 'Root', 0),
    folder('target', 'Target', 0, 'root'),
    folder('sibling', 'Sibling', 1, 'root'),
    folder('other-root', 'Other root', 1),
  ];
  const entries = [entry('target-entry', 'target', 'Target entry', 0)];
  const snapshot = hydrateBootstrap(compactPayload(folders, entries));
  const rootBefore = snapshot.tree[0];
  const targetBefore = rootBefore.children[0];
  const siblingBefore = rootBefore.children[1];
  const otherRootBefore = snapshot.tree[1];
  const updatedFolder = { ...folders[1], review_enabled: false };

  const updated = updateBootstrapFolder(snapshot, updatedFolder);

  assert.notStrictEqual(updated, snapshot);
  assert.notStrictEqual(updated.folders, snapshot.folders);
  assert.strictEqual(updated.folders[0], snapshot.folders[0]);
  assert.equal(updated.folders[1].review_enabled, false);
  assert.strictEqual(updated.entries, snapshot.entries);
  assert.notStrictEqual(updated.tree, snapshot.tree);
  assert.notStrictEqual(updated.tree[0], rootBefore);
  assert.notStrictEqual(updated.tree[0].children[0], targetBefore);
  assert.equal(updated.tree[0].children[0].review_enabled, false);
  assert.strictEqual(updated.tree[0].children[0].entries, targetBefore.entries);
  assert.strictEqual(updated.tree[0].children[0].children, targetBefore.children);
  assert.strictEqual(updated.tree[0].children[1], siblingBefore);
  assert.strictEqual(updated.tree[1], otherRootBefore);
  assert.strictEqual(updated.review, snapshot.review);
  assert.strictEqual(updated.git, snapshot.git);
});

test('an update for an unknown folder preserves the complete snapshot identity', () => {
  const folders = [folder('root', 'Root', 0)];
  const snapshot = hydrateBootstrap(compactPayload(folders, []));

  assert.strictEqual(
    updateBootstrapFolder(snapshot, folder('missing', 'Missing', 0)),
    snapshot,
  );
});
