**Answer.** The approximation is $149/750$ (about $0.1986667$); the absolute error is at most $(0.2)^5/120=1/375000$.

**Pattern cue.** The fourth-degree coefficient is zero, but the degree-four remainder still uses derivative five.

**Fast route.** The degree-four polynomial is $x-x^3/6$; at $x=1/5$ it gives $1/5-1/750=149/750$. The fifth derivative is $\cos x$, bounded by $1$ in magnitude. The error is therefore at most $0.2^5/5!=1/375000$.

**Trap check.** Do not force a nonzero $x^4$ coefficient; the degree-four Taylor polynomial may have actual degree three.

**Recall targets.** @gre:mathematics-subject-test:calculus:single-variable-differential-calculus:th:taylor-remainder.
