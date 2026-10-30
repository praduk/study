**Definitions and results used:** @[Sylow containment, number restrictions, and normalizer indices]mt3-sylow; @[Groups of prime-square order are abelian]mt3-pgroups; @[Faithful small-index coset actions of simple groups]mt3-actions; @[Normalizers and Lagrange's theorem]mt3-foundations.

**Technique:** Use a small normalizer to find P, enlarge through a Sylow group containing P, then force the original Q to be normal in the enlarged normalizer.

Suppose $G$ is simple. Sylow gives $n_{13}=105$, so $N_G(Q)$ has order $91=7\cdot13$. Both its Sylow subgroups are unique: their numbers divide $13$ or $7$ and satisfy the corresponding congruence. Hence $P$ has order $7$ and $Q\le N_G(P)$.

Choose $T\in\Syl_7(G)$ containing $P$. Since $|T|=49$, $T$ is abelian and normalizes $P$. Therefore $7^2\cdot13=637$ divides $|N_G(P)|$, and $[G:N_G(P)]$ divides $15$.

The normalizer is proper, because a normal subgroup $P$ would contradict simplicity. Indices $3$ and $5$ are impossible: the corresponding faithful coset action would embed $G$ in $S_3$ or $S_5$, whose orders are not divisible by $13$. Thus the index is $15$ and $|N_G(P)|=637$.

Inside $N_G(P)$ the Sylow $13$-number divides $49$ and is $1\pmod{13}$, so it is $1$. Thus $Q\nsubg N_G(P)$, giving $N_G(P)\le N_G(Q)$. This contradicts $637>91$.
