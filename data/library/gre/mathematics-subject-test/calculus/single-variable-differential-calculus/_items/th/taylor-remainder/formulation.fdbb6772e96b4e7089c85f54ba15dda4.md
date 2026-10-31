If $f$ has continuous derivatives through order $n+1$ on the segment joining $a,x$, then

$$
f(x)=\sum_{k=0}^{n}\frac{f^{(k)}(a)}{k!}(x-a)^k+\frac{f^{(n+1)}(c)}{(n+1)!}(x-a)^{n+1}
$$

for some $c$ between $a$ and $x$. Thus a bound $|f^{(n+1)}|\le M$ gives error at most $M|x-a|^{n+1}/(n+1)!$.

**Trap.** The error uses the next derivative and the next factorial. Existence of all derivatives alone does not guarantee equality to the infinite Taylor series.

**Practice different uses.** @gre:mathematics-subject-test:calculus:single-variable-differential-calculus:pb:taylor-sine-error; @gre:mathematics-subject-test:calculus:single-variable-differential-calculus:pb:linearization-error-bound.

**Contrasting practice.** @gre:mathematics-subject-test:calculus:single-variable-differential-calculus:pb:exponential-polynomial-error.
