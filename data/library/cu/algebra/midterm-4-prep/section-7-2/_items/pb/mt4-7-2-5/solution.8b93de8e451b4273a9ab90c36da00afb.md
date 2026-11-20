**Strategy.** For the field claim, check the ring operations and factor the lowest power of $x$ out of each nonzero series to build its inverse. For the valuation, track the first nonzero coefficient under multiplication and addition.

**(a) Verify the commutative ring structure.** For series with exponents bounded below by $N$ and $M$, the @[Laurent series operations]mt4-laurent-series give lower bounds $\min(N,M)$ for their sum and $N+M$ for their product. In the coefficient of $x^k$ in the product, the first index $i$ ranges only from $N$ to $k-M$. Each coefficient is therefore a finite sum in $F$.

Addition and negatives are coefficientwise. Interchanging the two indices in a product coefficient proves commutativity. Associativity and distributivity follow by regrouping finite sums in $F$ (in a triple product the three indices have fixed sum and are bounded below). The constant series $0$ and $1$ are the two identities. This verifies the @[commutative ring axioms]mt4-ring, and $1\ne0$ since $F$ is a @[field]mt4-field.

**(a) Construct inverses.** Let $f\ne0$ have least exponent $N$ and write $f=x^N u$. Then $u\in F[[x]]$ and its constant coefficient is the first nonzero coefficient of $f$. That coefficient is invertible in $F$. By the @[power series unit criterion]mt4-power-series-unit, $u$ has an inverse in $F[[x]]$. Hence $x^{-N}u^{-1}\in F((x))$ is an inverse of $f$, proving that $F((x))$ is a field.

**(b) Verify the valuation axioms.** Take nonzero $f,g$ with least exponents $N=v(f)$ and $M=v(g)$. The @[definition of a discrete valuation]mt4-discrete-valuation requires the following three checks.

- **Products.** The coefficient of $x^{N+M}$ in $fg$ is the product of the first nonzero coefficients of $f$ and $g$. It is nonzero because @[a field is an integral domain]gre:mathematics-subject-test:abstract-algebra:th:field-domain. Every earlier coefficient vanishes, so $v(fg)=N+M$.
- **Sums.** All coefficients of $f+g$ below $\min(N,M)$ vanish. If $f+g\ne0$, its first nonzero coefficient therefore occurs at or above that degree, giving $v(f+g)\ge\min(N,M)$.
- **Surjectivity.** For every $k\in\Z$, the monomial $x^k$ satisfies $v(x^k)=k$.

**Identify the valuation ring.** A nonzero series has nonnegative valuation exactly when it has no negative powers of $x$. Including zero gives precisely the @[formal power series ring]mt4-power-series $F[[x]]$.
