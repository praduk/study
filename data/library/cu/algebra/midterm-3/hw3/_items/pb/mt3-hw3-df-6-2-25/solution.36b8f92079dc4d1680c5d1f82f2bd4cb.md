**Definitions and results used:** @[Feit–Thompson odd-order theorem]cu:algebra:midterm-3:central:th:mt3-feit-thompson; @[A finite simple solvable group has prime order]cu:algebra:midterm-3:central:th:mt3-simple-solvable; @[Sylow theorem]cu:algebra:midterm-3:sylow:th:mt3-sylow; @[Unique, normal, and characteristic Sylow subgroups]cu:algebra:midterm-3:sylow:th:mt3-sylow-normality; @[Counting distinct prime-order subgroups]cu:algebra:midterm-3:sylow:th:mt3-prime-order-intersections; @[Regular action]cu:algebra:midterm-3:foundations:df:mt3-regular-action; @[Sign is a homomorphism]cu:algebra:midterm-3:foundations:th:mt3-sign-homomorphism; @[Faithful actions of simple groups and the alternating-group obstruction]cu:algebra:midterm-3:foundations:th:mt3-simple-actions; @[A nontrivial finite p-group has nontrivial center]cu:algebra:midterm-3:sylow:th:mt3-pgroups; @[Cauchy’s theorem]cu:algebra:midterm-3:foundations:th:mt3-cauchy; @[Abelian simple groups have prime order]cu:algebra:midterm-3:foundations:th:mt3-abelian-simple.

**Technique:** Use permitted Feit–Thompson only for odd order; then largest-prime Sylow counts and a small-degree action force the arithmetic.

**1. Reduce to even order.** The order is composite. If it were odd, Feit–Thompson would make $G$ solvable; a finite simple solvable group is cyclic of prime order, a contradiction. This is the only use of Feit–Thompson.

**2. Deal with the possible powers of $2$, including repeated primes.**

- An order $2m$ with $m$ odd is impossible. In the left regular action, an involution acts as $m$ disjoint transpositions. The sign homomorphism is therefore onto $C_2$, with a proper nontrivial kernel.
- An order $16$ is impossible because a nontrivial finite $2$-group has nontrivial center and cannot be simple unless it has prime order.
- For order $8s$ with $s$ odd prime, $n_s>1$ divides $8$ and is $1\pmod s$. Thus either $s=3,n_s=4$, or $s=7,n_s=8$. In order $24$, the faithful action of a simple group on four Sylow $3$-subgroups would land in $A_4$: its sign map must be trivial. But $24\nmid12$. In order $56$, the $8\cdot6=48$ elements of order $7$ leave exactly $8$ elements, forcing a unique Sylow $2$-subgroup.
- For order $4s^2$ with $s$ odd prime, $n_s>1$ divides $4$ and is $1\pmod s$, forcing $s=3,n_s=4$. Order $36$ cannot embed in $S_4$.

The only remaining form is $|G|=4qr$ with distinct odd primes $q<r$.

**3. Use the largest prime and count.** Since $n_r>1$ divides $4q$ and $n_r\equiv1\pmod r$, the only possibilities are $n_r=2q$ or $4q$ (the divisors $2,4,q$ are excluded by $r>q\ge3$).

If $n_r=4q$, its subgroups account for $4q(r-1)$ nonidentity elements, leaving $4q$ elements including the identity. Thus

$$
n_q(q-1)\le4q-1.
$$

Since $n_q\ge q+1$, this implies $q^2\le4q$, so $q=3$. The same inequality then forces $n_q=4$. But a faithful degree-$4$ action is impossible since $r>3$ divides $|G|$ and not $4!$.

Hence $n_r=2q$. The congruence $r\mid2q-1$, together with $r>q$, gives $r=2q-1$. The nontrivial divisors of $4r$ eligible for $n_q$ are $4,r,2r,4r$; the divisor $2$ is excluded. Modulo $q$ these are $4,-1,-2,-4$. For one to equal $1$, the odd prime $q$ must be $3$ or $5$. If $q=5$, then $r=9$ is not prime. Therefore $q=3$, $r=5$, and $|G|=60$.

This proves the necessary order; it does not by itself classify simple groups of that order.
