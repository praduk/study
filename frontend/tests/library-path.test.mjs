import assert from 'node:assert/strict';
import test from 'node:test';

import {
  folderPathIds,
  libraryPathForEntry,
  resolveLibraryPath,
} from '../lib/library-path.ts';

const entry = {
  id: 'lagrange',
  folder_id: 'algebra',
  kind: 'th',
  title: "Lagrange's theorem",
  tag: 'lagrange',
  header: '',
  order: 0,
  canonical_tag: 'math:algebra:th:lagrange',
  review_modes: ['statement', 'proof-plan'],
  formulations: [
    { id: 'standard', label: 'Standard', subtag: null, file: 'standard.md', main: true },
    { id: 'action', label: 'Action', subtag: 'action', file: 'action.md', main: false },
  ],
  supplements: [
    { id: 'proof', label: 'Standard', subtag: null, file: 'proof.md', main: true, kind: 'pf' },
    { id: 'orbit-proof', label: 'Orbits', subtag: 'orbits', file: 'orbits.md', main: false, kind: 'pf' },
  ],
  assets: [],
};

test('canonical entry and variant tags round-trip as browser paths', () => {
  assert.equal(libraryPathForEntry(entry), '/library/math/algebra/th/lagrange');
  assert.equal(libraryPathForEntry(entry, 'standard'), '/library/math/algebra/th/lagrange');
  assert.equal(libraryPathForEntry(entry, 'action'), '/library/math/algebra/th/lagrange/action');
  assert.equal(libraryPathForEntry(entry, 'proof'), '/library/math/algebra/th/lagrange/pf');
  assert.equal(libraryPathForEntry(entry, 'orbit-proof'), '/library/math/algebra/th/lagrange/pf/orbits');

  assert.deepEqual(resolveLibraryPath('/library/math/algebra/th/lagrange', [entry]), {
    kind: 'entry', entry, variantId: null, canonicalPath: '/library/math/algebra/th/lagrange',
  });
  assert.equal(resolveLibraryPath('/library/math/algebra/th/lagrange/action', [entry]).variantId, 'action');
  assert.equal(resolveLibraryPath('/library/math/algebra/th/lagrange/pf', [entry]).variantId, 'proof');
  assert.equal(resolveLibraryPath('/library/math/algebra/th/lagrange/pf/orbits/', [entry]).variantId, 'orbit-proof');
});

test('root, unknown, and malformed paths are distinguished', () => {
  assert.deepEqual(resolveLibraryPath('/', [entry]), { kind: 'root' });
  for (const path of [
    '/library',
    '/library/math/algebra/th/unknown',
    '/library/math//th/lagrange',
    '/library/Math/algebra/th/lagrange',
    '/library/math%3Aalgebra/th/lagrange',
    '/library/%E0%A4%A',
    '/api/entries/lagrange',
  ]) {
    assert.deepEqual(resolveLibraryPath(path, [entry]), { kind: 'missing' });
  }
});

test('only the selected folder ancestry is expanded initially', () => {
  const folders = [
    { id: 'math', parent_id: null },
    { id: 'algebra', parent_id: 'math' },
    { id: 'groups', parent_id: 'algebra' },
    { id: 'analysis', parent_id: 'math' },
    { id: 'unrelated', parent_id: null },
  ];

  assert.deepEqual([...folderPathIds('groups', folders)].sort(), ['algebra', 'groups', 'math']);
});
