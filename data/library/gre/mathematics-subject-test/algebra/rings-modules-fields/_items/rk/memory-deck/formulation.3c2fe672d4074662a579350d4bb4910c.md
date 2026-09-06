## Ring hierarchy

For the usual commutative-with-unity conventions:

$$
\text{field}\Longrightarrow\text{integral domain}\Longrightarrow\text{commutative ring with }1.
$$

Every finite integral domain is a field. The converses fail. In $\mathbb Z/n\mathbb Z$, $[a]$ is a unit iff $\gcd(a,n)=1$; it is a nonzero zero divisor iff $1<\gcd(a,n)<n$.

## Ideals and quotients

Kernels of ring homomorphisms are ideals, and

$$
R/\ker\phi\cong\operatorname{im}\phi.
$$

For a commutative ring with $1$ and a proper ideal $I$,

$$
I\text{ prime}\iff R/I\text{ is an integral domain},
$$

$$
I\text{ maximal}\iff R/I\text{ is a field}.
$$

Every maximal ideal is prime; the converse need not hold.

In $\mathbb Z$, every ideal is $n\mathbb Z$. In $F[x]$, ideals are principal and Euclidean division gives $f=qg+r$ with $\deg r<\deg g$.

## Polynomial recognition

The remainder on division by $x-a$ is $f(a)$, and $f(a)=0$ iff $x-a$ divides $f$. Over a field, a polynomial of degree $2$ or $3$ is reducible iff it has a root. For higher degree, no-root does not imply irreducible.

If $p(x)$ is irreducible over $F$, then $F[x]/(p)$ is a field with $|F|^{\deg p}$ elements when $F$ is finite.

## Modules

An $R$-module generalizes a vector space by allowing scalars from a ring. A submodule is an additive subgroup closed under scalar multiplication. For $m\in M$,

$$
\operatorname{Ann}_R(m)=\{r\in R:rm=0\}
$$

is an ideal. A cyclic module has form $Rm$ and is isomorphic to $R/\operatorname{Ann}(m)$.

Over a PID, finitely generated modules split into a free part and cyclic torsion parts; for GRE-speed questions, recognize $\mathbb Z$-modules as abelian groups and compute orders or annihilators directly.

## Fields and extensions

For $F\subseteq K\subseteq L$ with finite degrees,

$$
[L:F]=[L:K][K:F].
$$

If $m_\alpha$ is the minimal polynomial of $\alpha$ over $F$, then

$$
[F(\alpha):F]=\deg m_\alpha.
$$

A finite field has order $p^n$, and $\mathbb F_q^\times$ is cyclic of order $q-1$.

## Traps

State whether rings require unity and commutativity. A quotient $R/I$ needs $I$ an ideal, not merely a subring. Irreducibility depends on the base field.
