**Strategy.** Compute each quotient by setting the generators of its ideal equal to zero. The ideal is @[prime exactly when the quotient is a domain]mt4-prime-quotient-domain and @[maximal exactly when the quotient is a field]mt4-maximal-quotient-field.

**1. Set $x=0$.** What remains is a polynomial in $y$. To see exactly why, write the ring as the @[iterated polynomial ring]mt4-polynomials-several-variables $\Q[x][y]$. On the coefficient ring $\Q[x]$, evaluation at zero is onto $\Q$ and has kernel $(x)$, since a polynomial vanishes at zero exactly when $x$ divides it. The @[first isomorphism theorem]mt4-first-isomorphism and @[coefficient reduction]mt4-polynomial-coefficient-quotient give

$$
\Q[x,y]/(x)\isoto\bigl(\Q[x]/(x)\bigr)[y]\isoto\Q[y].
$$

The ring $\Q[y]$ is a domain, and its only units are nonzero constants by the @[polynomial domain and unit theorem]mt4-polynomial-domains. In particular $y$ has no inverse. Thus **$(x)$ is prime and is not maximal**.

**2. Set $x=y=0$.** Evaluation at the origin takes $\Q[x,y]$ onto $\Q$. Its @[kernel is an ideal]mt4-kernel-image containing $x$ and $y$, so it contains the @[ideal they generate]mt4-principal-ideal. For the reverse inclusion, a polynomial in the kernel has zero constant term. Each remaining monomial is divisible by $x$ or $y$, so the polynomial lies in $(x,y)$.

The kernel is therefore $(x,y)$ and the quotient is isomorphic to $\Q$. This is a field, hence @[a domain]gre:mathematics-subject-test:abstract-algebra:th:field-domain. Thus **$(x,y)$ is both maximal and prime**.
