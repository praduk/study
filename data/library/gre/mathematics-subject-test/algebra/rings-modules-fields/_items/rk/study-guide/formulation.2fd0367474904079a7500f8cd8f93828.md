## Rings and fields

- In $\mathbb Z/n\mathbb Z$, $[a]$ is a unit exactly when $\gcd(a,n)=1$. A nonzero class with nontrivial gcd is a zero divisor when $n$ is composite.
- Ideals are kernels of ring homomorphisms. The quotient $R/I$ is a field exactly when $I$ is maximal, and is an integral domain exactly when $I$ is prime, for commutative rings with identity.
- Over a field $F$, $F[x]/(p)$ is a field exactly when $p$ is irreducible. A quadratic or cubic over $F$ is irreducible exactly when it has no root in $F$.
- In a polynomial ring over a field, division, gcd calculations, and the Euclidean algorithm work much as they do for integers.

## Modules

- An $R$-module is an abelian group with compatible scalar multiplication by $R$. Vector spaces are precisely modules over a field, but modules over general rings need not have bases.
- A submodule must contain zero and be closed under addition and scalar multiplication. For an element $m$, its cyclic submodule is $Rm$, and its annihilator is the ideal $\operatorname{Ann}_R(m)=\{r\in R:rm=0\}$.
- Quotient modules use submodules just as quotient groups use normal subgroups. Homomorphism kernel/image and isomorphism theorems carry over.

## Recognition cues and traps

In finite quotient problems, reduce coefficients immediately and exploit gcds. In $F[x]/(p)$, replace powers using the defining relation before solving for an inverse. Do not call a quotient a field merely because it is finite, and do not import vector-space basis claims into arbitrary modules.
