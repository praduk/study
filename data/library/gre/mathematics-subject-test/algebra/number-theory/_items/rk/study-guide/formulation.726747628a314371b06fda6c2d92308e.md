## Core facts

- Use the Euclidean algorithm for $\gcd(a,b)$ and back-substitution for Bezout coefficients. The equation $ax+by=c$ has integer solutions exactly when $\gcd(a,b)$ divides $c$.
- Congruences support addition and multiplication. Cancellation by $c$ modulo $n$ is valid without changing the modulus only when $\gcd(c,n)=1$.
- The Chinese remainder theorem gives a unique class modulo the product for pairwise coprime moduli. First look for a shared simple residue such as $-1$ before constructing inverses.
- Unique prime factorization drives divisor counts: if $n=\prod p_i^{a_i}$, then the number of positive divisors is $\prod(a_i+1)$ and $\varphi(n)=n\prod_{p\mid n}(1-1/p)$.
- Fermat gives $a^{p-1}\equiv1\pmod p$ when $p\nmid a$; Euler gives $a^{\varphi(n)}\equiv1\pmod n$ when $\gcd(a,n)=1$. The actual power cycle may be shorter.

## Recognition cues and traps

Reduce early, seek short cycles, factor the modulus when useful, and test gcd solvability before solving a congruence or Diophantine equation. Do not divide in modular arithmetic without checking invertibility, apply Euler when the base is not coprime to the modulus, or assume separate congruences are compatible when moduli share factors.
