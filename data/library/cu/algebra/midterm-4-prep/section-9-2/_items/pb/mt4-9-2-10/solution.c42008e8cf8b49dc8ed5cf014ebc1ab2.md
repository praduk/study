Use @[polynomial division]mt4-division-polynomials and the @[Euclidean algorithm]mt4-euclidean-gcd. Write $q=x^2-4x+15$ and $c=10x^2+9x-19$. The first two divisions, with nonzero rational factors cleared, give

$$
\begin{aligned}
b&=q\,a-5c,\\
100a&=(10x+31)c+11(x-1).
\end{aligned}
$$

The next division is exact: $c=(10x+19)(x-1)$. Thus the last nonzero remainder, normalized to be @[monic]mt4-polynomial-ring, is $x-1$. Substituting $5c=q\,a-b$ into the second line gives

$$
55(x-1)=\bigl(500-(10x+31)q\bigr)a+(10x+31)b.
$$

Hence $A=(-10x^3+9x^2-26x+35)/55$ and $B=(10x+31)/55$. As a check, $a(1)=b(1)=0$, so $x-1$ divides both; the displayed identity forces every common divisor to divide $x-1$.
