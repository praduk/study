**Strategy.** Use @[induction on the exponent]math:set:naturals-recursion:th:natural-induction. When multiplying by $a+b$, track which two terms contribute to the same power of $a$. Their multiplicities combine by Pascal’s identity.

**Interpret the coefficients.** Regard each nonnegative integer $m$ as the ring element $m\,1_R$, the sum of $m$ copies of $1_R$, with $0\,1_R=0$. By the @[ring laws]mt4-ring, multiplying by $m\,1_R$ adds an element to itself $m$ times. This is how $\binom nk$ acts in $R$.

**Start at $n=0$.** The left side is $1_R$. The only term on the right is $\binom00 a^0 b^0=1_R$.

**Pass from $n$ to $n+1$.** Assume the formula at $n$. Multiply that expansion by $a+b$ and distribute. Since $a$ and $b$ commute, for each $1\le k\le n$ the term $a^k b^{n+1-k}$ receives exactly two contributions, indexed by how many copies of $a$ were present before multiplication.

- Multiplying an old $a^{k-1}b^{n+1-k}$ term by $a$ contributes $\binom n{k-1}$ copies.
- Multiplying an old $a^k b^{n-k}$ term by $b$ contributes $\binom nk$ copies.

The combined multiplicity is $\binom n{k-1}+\binom nk=\binom{n+1}k$ by @[Pascal’s identity]gre:mathematics-subject-test:discrete-mathematics:th:pascal-identity. The end terms $b^{n+1}$ and $a^{n+1}$ each occur once. We have obtained every term of the claimed expansion at $n+1$, completing the induction.
