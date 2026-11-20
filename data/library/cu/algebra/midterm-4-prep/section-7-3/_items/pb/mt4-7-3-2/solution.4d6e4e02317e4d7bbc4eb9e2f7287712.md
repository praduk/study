**Strategy.** Count the @[units]mt4-unit of the two polynomial rings. A @[ring isomorphism]mt4-ring-isomorphism induces a @[bijection of unit groups]mt4-units-under-isomorphism, so different counts will rule out an isomorphism.

**Identify the possible polynomial units.** Both $\Z$ and $\Q$ are @[integral domains]mt4-integral-domain. The @[polynomial unit theorem]mt4-polynomial-degree-product therefore says that a polynomial over either ring is a unit exactly when it is a constant that is invertible in the coefficient ring.

**Count in each ring.**

- In $\Z$, $ab=1$ forces $|a|=|b|=1$. Both $1$ and $-1$ are their own inverses, so $\Z[x]$ has exactly two units.
- Since $\Q$ is a @[field]mt4-field, every nonzero rational number is a unit. Thus $\Q[x]$ has infinitely many units.

There is no bijection between these two sets of units. Hence $\Z[x]$ and $\Q[x]$ cannot be isomorphic.
