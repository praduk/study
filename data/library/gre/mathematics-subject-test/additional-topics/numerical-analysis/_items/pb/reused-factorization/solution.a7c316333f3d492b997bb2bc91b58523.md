**Answer.** $O(n^3+mn^2)$.

**Pattern cue.** Separate setup cost from cost per right-hand side.

**Fast route.** Factor once in $O(n^3)$, then use forward/back substitution in $O(n^2)$ for each of the $m$ vectors.

**Trap.** Refactoring independently for every right-hand side wastes the shared structure.

**Recall.** @gre:mathematics-subject-test:additional-topics:numerical-analysis:rk:linear-solves.
