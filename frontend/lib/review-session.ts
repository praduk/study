export interface ReviewQueueAdvance<T> {
  cards: T[];
  nextIndex: number;
  batchExhausted: boolean;
}

/** Advance one graded card and place an Again retry later in the current batch. */
export function advanceReviewQueue<T>(
  cards: readonly T[],
  index: number,
  retry: { card: T; afterItems: number } | null,
): ReviewQueueAdvance<T> {
  const nextCards = [...cards];
  if (retry) {
    const insertion = Math.min(nextCards.length, index + 1 + Math.max(0, retry.afterItems));
    nextCards.splice(insertion, 0, retry.card);
  }
  const nextIndex = index + 1;
  return { cards: nextCards, nextIndex, batchExhausted: nextIndex >= nextCards.length };
}
