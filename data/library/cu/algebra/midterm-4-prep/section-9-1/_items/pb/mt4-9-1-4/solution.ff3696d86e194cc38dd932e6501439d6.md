**The ideal $(x)$.** Regard $\Q[x,y]$ as $\Q[x][y]$ by @[the iterated polynomial ring definition]mt4-polynomials-several-variables. Evaluation at $x=0$ takes $\Q[x]$ onto $\Q$ with kernel $(x)$, since a polynomial has zero constant term exactly when it is a multiple of $x$. By the @[first isomorphism theorem]mt4-first-isomorphism and then @[coefficient reduction]mt4-polynomial-coefficient-quotient,

$$
\Q[x,y]/(x)\isoto\bigl(\Q[x]/(x)\bigr)[y]\isoto\Q[y].
$$

This quotient is a domain. Its element $y$ has no inverse by @[the polynomial unit criterion]mt4-polynomial-domains, so it is not a field. The @[prime]mt4-prime-quotient-domain and @[maximal]mt4-maximal-quotient-field quotient criteria give the verdict: $(x)$ is prime but not maximal.

**The ideal $(x,y)$.** Evaluation at $(0,0)$ takes $\Q[x,y]$ onto $\Q$. Its @[kernel is an ideal]mt4-kernel-image and contains $x$ and $y$, hence contains the @[ideal they generate]mt4-principal-ideal. Conversely, a polynomial in the kernel has zero constant term, so each of its monomials is divisible by $x$ or $y$. This proves that the kernel is $(x,y)$. The quotient is therefore isomorphic to $\Q$, which is both a field and @[an integral domain]gre:mathematics-subject-test:abstract-algebra:th:field-domain. By the same two criteria, $(x,y)$ is maximal and prime.
