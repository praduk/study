**Euclidean algorithm.** Use @[polynomial division]mt4-division-polynomials. Write $q=x^2-4x+15$ and $c=10x^2+9x-19$. The divisions yield the following identities with denominators cleared:

$$
\begin{aligned}
b&=qa-5c,\\
100a&=(10x+31)c+11(x-1),\\
c&=(10x+19)(x-1).
\end{aligned}
$$

Nonzero rational constants are @[units in the polynomial ring]mt4-polynomial-domains, so rescaling these remainders preserves their common divisors. The @[Euclidean algorithm]mt4-euclidean-gcd gives $x-1$ as the last nonzero remainder after @[monic normalization]mt4-polynomial-ring.

**Bézout identity.** Substitute $5c=qa-b$ into the second line:

$$
55(x-1)=\bigl(500-(10x+31)q\bigr)a+(10x+31)b.
$$

Consequently $Aa+Bb=x-1$ for

$$
A=\frac{-10x^3+9x^2-26x+35}{55},\qquad B=\frac{10x+31}{55}.
$$

As a check, $a(1)=b(1)=0$, so $x-1$ divides both by @[the factor theorem]gre:mathematics-subject-test:abstract-algebra:th:remainder-factor. Every common divisor divides $Aa+Bb=x-1$, which verifies the @[defining property of the gcd]mt4-divisibility-gcd.
