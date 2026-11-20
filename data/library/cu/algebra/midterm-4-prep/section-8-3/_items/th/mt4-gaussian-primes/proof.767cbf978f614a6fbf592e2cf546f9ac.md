In $\Z[i]$ the @[norm]mt4-quadratic-integers-norm is $N(a+bi)=a^2+b^2$. It is @[multiplicative and detects units]mt4-quadratic-norm-units. A nonunit factor of a nonzero element has integer norm at least $2$. Thus every element of prime norm is @[irreducible]mt4-irreducible.

**The prime $2$.** Direct multiplication gives $2=-i(1+i)^2$. Here $N(1+i)=2$.

**Primes $q\equiv3\pmod4$.** If $q$ factored into two nonunits, their norms would multiply to $q^2$, so both would equal $q$. But no $a^2+b^2$ is $3$ modulo $4$, since integer squares are $0$ or $1$ modulo $4$. Thus $q$ remains irreducible.

**Primes $p\equiv1\pmod4$.** Write $p=4m+1$. We first find an integer $n$ with $n^2\equiv-1\pmod p$. The @[unit criterion for residue classes]math:num:congruences:th:linear-congruence makes every nonzero residue modulo $p$ invertible. In the field $\Z/p\Z$, the only elements equal to their own inverse are the @[square roots of one]mt4-7-1-11, namely $\pm1$. Pairing all other residues with their inverses gives $(p-1)!\equiv-1\pmod p$. Pairing $k$ with $p-k$ instead gives $(p-1)!\equiv(-1)^{2m}((2m)!)^2\pmod p$. Take $n=(2m)!$.

Now $p$ divides $(n+i)(n-i)$ but divides neither factor in $\Z[i]$, since their imaginary coefficients are $\pm1$. Hence $p$ is not a @[prime element]mt4-prime-element. By @[Gaussian division]mt4-gaussian-division and @[the Euclidean principal ideal theorem]mt4-euclidean-principal, $\Z[i]$ is a PID. Since an irreducible there is @[prime]mt4-pid-prime-irreducible, $p$ splits into nonunits. Their norms must both be $p$. For either factor $\pi=a+bi$ we therefore have $p=\pi\bar\pi$, and both factors are irreducible by their prime norms.

The Gaussian units are $\pm1,\pm i$, the four solutions to $N(u)=1$. If $\pi$ and $\bar\pi$ were @[associates]mt4-associates, multiplying $a+bi$ by one of these four units would give $a-bi$. This requires $a=0$, $b=0$, or $a=\pm b$. Then $p=a^2+b^2$ would be a square or twice a square, impossible for this odd prime.

**Exhaustion.** Any Gaussian irreducible $z$ is prime in this PID and divides the positive integer $N(z)=z\bar z>1$. Factor $N(z)$ into @[ordinary integer primes]math:num:divisibility:th:prime-factorization. By primality, $z$ divides one of them. The three cases above factor each such prime into Gaussian irreducibles. Applying primality once more, $z$ divides a listed irreducible, hence is its associate.
