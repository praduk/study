**Answer.** Approximation $1.105$; error at most $1/3000$.

**Pattern cue.** Use the next derivative bound and the next factorial.

**Fast route.** The polynomial is $1+x+x^2/2$, giving $1.105$. The third derivative is $e^t\le2$, so the error is at most $2(0.1)^3/3!=1/3000$.

**Trap check.** The degree-two polynomial requires a third-derivative remainder, not a second-derivative remainder.

**Recall target.** @gre:mathematics-subject-test:calculus:single-variable-differential-calculus:th:taylor-remainder.
