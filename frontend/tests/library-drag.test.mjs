import assert from 'node:assert/strict';
import test from 'node:test';

import { acceptLibraryDrag, LIBRARY_DRAG_TYPE } from '../lib/library-drag.ts';

function dragEvent(type, types) {
  return {
    type,
    defaultPrevented: false,
    propagationStopped: false,
    currentTarget: { classList: new Set() },
    // Browsers protect payload contents until drop. Acceptance must use types.
    dataTransfer: { types, dropEffect: 'none', getData() { throw new Error('Protected drag data'); } },
    preventDefault() { this.defaultPrevented = true; },
    stopPropagation() { this.propagationStopped = true; },
  };
}

for (const type of ['dragenter', 'dragover']) {
  test(`${type} accepts an internal move without reading protected payload data`, () => {
    const event = dragEvent(type, [LIBRARY_DRAG_TYPE]);
    acceptLibraryDrag(event);
    assert.equal(event.defaultPrevented, true);
    assert.equal(event.propagationStopped, true);
    assert.equal(event.dataTransfer.dropEffect, 'move');
    assert.equal(event.currentTarget.classList.has('drop-target'), true);
  });
}

test('external text and file drags are not advertised as library moves', () => {
  for (const types of [[], ['text/plain'], ['Files']]) {
    const event = dragEvent('dragenter', types);
    acceptLibraryDrag(event);
    assert.equal(event.defaultPrevented, false);
    assert.equal(event.propagationStopped, false);
    assert.equal(event.dataTransfer.dropEffect, 'none');
    assert.equal(event.currentTarget.classList.size, 0);
  }
});
