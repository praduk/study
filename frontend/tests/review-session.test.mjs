import assert from 'node:assert/strict';
import test from 'node:test';

import {
  advanceReviewQueue,
  reviewAttemptSubmission,
} from '../lib/review-session.ts';

test('phone and blank desktop responses are think-only attempts', () => {
  assert.deepEqual(reviewAttemptSubmission('written on a phone', true), {
    attempt: '',
    overt: false,
  });
  assert.deepEqual(reviewAttemptSubmission('   ', false), {
    attempt: '',
    overt: false,
  });
  assert.deepEqual(reviewAttemptSubmission('A written answer', false), {
    attempt: 'A written answer',
    overt: true,
  });
});

test('the end of a review batch requires a fresh queue check', () => {
  const result = advanceReviewQueue(['first', 'last'], 1, null);

  assert.deepEqual(result.cards, ['first', 'last']);
  assert.equal(result.nextIndex, 2);
  assert.equal(result.batchExhausted, true);
});

test('an Again retry keeps the current batch active', () => {
  const result = advanceReviewQueue(
    ['current'],
    0,
    { card: 'retry', afterItems: 3 },
  );

  assert.deepEqual(result.cards, ['current', 'retry']);
  assert.equal(result.nextIndex, 1);
  assert.equal(result.batchExhausted, false);
});

test('an Again retry is inserted after the requested number of queued cards', () => {
  const result = advanceReviewQueue(
    ['current', 'one', 'two', 'three', 'four'],
    0,
    { card: 'retry', afterItems: 3 },
  );

  assert.deepEqual(result.cards, ['current', 'one', 'two', 'three', 'retry', 'four']);
});
