**Strategy.** Use division by $f$ to find a short representative of each class. Prove that representative is unique, then read off a basis from its coefficients.

**1. Existence.** For any $g\in F[x]$, @[polynomial division]mt4-division-polynomials gives $g=qf+r$ with $r=0$ or $\deg r<n$. Since $g-r\in(f)$, the remainder $r$ represents the same @[quotient class]mt4-quotient-ring as $g$.

**2. Uniqueness.** If $r$ and $s$ are two such representatives of the same class, then $r-s$ lies in the @[principal ideal]mt4-principal-ideal $(f)$. By the @[degree formula]mt4-polynomial-domains, every nonzero multiple of $f$ has degree at least $n$. But $r-s$ is zero or has degree less than $n$. Hence $r-s=0$.

**3. Spanning and linear independence.** The quotient is an $F$-vector space with $c\bar g=\overline{cg}$ for $c\in F$. This is well defined since $g-h\in(f)$ implies $c(g-h)\in(f)$, and the @[vector space laws]math:algebra:linear-foundations:df:vector-space follow from those in $F[x]$.

Write $r=c_0+c_1x+\cdots+c_{n-1}x^{n-1}$. Existence of $r$ says that $\bar 1,\bar x,\ldots,\overline{x^{n-1}}$ span the quotient. For linear independence, suppose a linear combination of these classes is zero. Its coefficient polynomial is a remainder representing the zero class. The zero polynomial is another such remainder, so uniqueness forces all the coefficients to vanish. The classes are linearly independent. They form a @[basis]math:algebra:linear-foundations:df:basis-dimension of size $n$, so the dimension is $n$.
