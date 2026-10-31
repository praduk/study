**Answer.** $a_n\to2$.

**Pattern cue.** Find an invariant interval and a signed increment.

**Fast route.** If $1\le a_n<2$, then $1\le a_{n+1}<2$ and $a_{n+1}-a_n=(2-a_n)/2>0$. Induction proves increasing and bounded, hence convergent. The limit satisfies $L=(L+2)/2$, giving $2$. Also $2-a_n=2^{1-n}$ verifies convergence directly.

**Trap check.** The fixed-point equation is used after proving convergence.

**Recall targets.** @gre:mathematics-subject-test:calculus:sequences-series-differential-equations:th:monotone-sequence.
