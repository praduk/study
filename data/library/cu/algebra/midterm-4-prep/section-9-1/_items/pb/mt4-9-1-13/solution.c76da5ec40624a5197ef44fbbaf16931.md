**Strategy.** Distinguish the two rings by a property preserved under isomorphism. Show that the first quotient is a domain. In the second, find two factors whose product vanishes and check that neither factor vanishes.

**1. Eliminate $x$ in the first quotient.** In the @[iterated polynomial ring]mt4-polynomials-several-variables $F[y][x]$, substitute $x=y^2$. The resulting @[ring homomorphism]mt4-ring-homomorphism fixes $F[y]$, so it is onto. Its kernel contains $x-y^2$.

For the reverse inclusion, every positive power satisfies the identity

$$
x^i-(y^2)^i=(x-y^2)\sum_{j=0}^{i-1}x^{i-1-j}(y^2)^j.
$$

Applying this to each power of $x$ in $h(x,y)$ shows that $h(x,y)-h(y^2,y)$ is divisible by $x-y^2$. If $h$ maps to zero, this difference is $h$ itself. Thus the kernel is $(x-y^2)=(y^2-x)$. By the @[first isomorphism theorem]mt4-first-isomorphism, the first quotient is isomorphic to $F[y]$, a @[domain]mt4-polynomial-domains.

**2. Find a zero divisor in the second quotient.** Write bars for classes modulo $y^2-x^2$. By @[coset multiplication]mt4-quotient-operations,

$$
\overline{y-x}\;\overline{y+x}=\overline{y^2-x^2}=0.
$$

A factor would vanish in the @[quotient]mt4-quotient-ring only if it belonged to the @[principal ideal]mt4-principal-ideal $(y^2-x^2)$. Both factors have degree one in $y$. Over the domain $F[x]$, every nonzero multiple of $y^2-x^2$ has degree at least two in $y$ by the @[degree formula]mt4-polynomial-domains. Both classes therefore survive. In characteristic two they coincide, giving a nonzero class whose square is zero.

**3. Compare the rings.** The second quotient has a @[zero divisor]mt4-zero-divisor. A @[ring isomorphism]mt4-ring-isomorphism preserves products and carries nonzero elements to nonzero elements, so a domain cannot be isomorphic to this quotient.
