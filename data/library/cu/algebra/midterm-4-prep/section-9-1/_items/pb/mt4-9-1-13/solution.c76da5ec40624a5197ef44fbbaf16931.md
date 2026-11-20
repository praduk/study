**First quotient.** Regard $F[x,y]$ as an @[iterated polynomial ring]mt4-polynomials-several-variables $F[y][x]$ and substitute $x=y^2$. This substitution preserves addition and multiplication and fixes $F[y]$, so it gives a surjective @[ring homomorphism]mt4-ring-homomorphism. Its kernel contains $x-y^2$. Conversely, for $i\ge1$, telescoping gives

$$
x^i-(y^2)^i=(x-y^2)\sum_{j=0}^{i-1}x^{i-1-j}(y^2)^j.
$$

Apply this identity term by term to see that $h(x,y)-h(y^2,y)$ belongs to $(x-y^2)$ for every $h$. If $h$ maps to zero, this difference is $h$ itself. The kernel is therefore $(x-y^2)=(y^2-x)$. By @[the first isomorphism theorem]mt4-first-isomorphism, the first quotient is isomorphic to $F[y]$, an integral domain by @[the polynomial domain theorem]mt4-polynomial-domains.

**Second quotient.** By @[coset multiplication]mt4-quotient-operations the classes of $y-x$ and $y+x$ multiply to zero, since their product before reduction is $y^2-x^2$. Both classes are nonzero. Indeed, for either to vanish in the @[quotient ring]mt4-quotient-ring, that degree-one polynomial in $y$ would have to lie in the @[principal ideal]mt4-principal-ideal $(y^2-x^2)$. Over the domain $F[x]$, every nonzero multiple of $y^2-x^2$ has $y$-degree at least two by @[the degree formula]mt4-polynomial-domains.

In characteristic two the classes coincide, so their common nonzero class has square zero. In every characteristic the second quotient has a @[zero divisor]mt4-zero-divisor. A @[ring isomorphism]mt4-ring-isomorphism preserves zero products and takes nonzero elements to nonzero elements. The first quotient is a domain, so these rings cannot be isomorphic.
