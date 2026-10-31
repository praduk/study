**Answer.** $n-1$ comparisons on increasing input; $\Theta(n^2)$ in the worst case.

**Pattern cue.** Best and worst cases differ.

**Fast route.** Each new element is already at least its predecessor, so one comparison ends that insertion. Reverse order requires comparisons against all earlier elements, totaling $n(n-1)/2$.

**Trap.** A worst-case bound does not describe every input.

**Recall.** @gre:mathematics-subject-test:additional-topics:graph-theory-algorithms:rk:search-sort.
