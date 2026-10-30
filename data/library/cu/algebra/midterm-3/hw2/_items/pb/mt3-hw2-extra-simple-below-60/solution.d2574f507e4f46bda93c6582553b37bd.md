**Definitions and results used:** @[Sylow counting, uniqueness, and prime-order intersection counting]mt3-sylow; @[faithful permutation actions of simple groups]mt3-actions; @[nontrivial center of a finite p-group]mt3-pgroups; @[simple groups, abelian simple groups, and Lagrange’s theorem]mt3-foundations.

**Technique:** Reduce to six exceptional orders, then use a tiny permutation action or count prime-order elements.

Use the convention that a simple group is nontrivial. If $|G|=p^a$, the center of a finite $p$-group is nontrivial; simplicity forces $Z(G)=G$. A finite abelian simple group is $C_p$, so this case is settled.

Assume instead that $G$ is nonabelian simple. Every Sylow subgroup is proper and nonnormal. For each prime $p\mid|G|$, the allowed Sylow numbers satisfy $n_p\mid|G|/|P|$ and $n_p\equiv1\pmod p$, with $n_p\ne1$.

**Exhaust the orders.** For every mixed-prime order below $60$ except $12,24,30,36,48,56$, the congruence and divisibility conditions alone force a normal Sylow subgroup. Here is the complete arithmetic check, listing the forced prime followed by the excluded orders:

- $p=3$: $6,18,54$.
- $p=5$: $10,15,20,40,45,50$.
- $p=7$: $14,21,28,35,42$.
- $p=11$: $22,33,44,55$.
- $p=13$: $26,39,52$.
- $p=17$: $34,51$.
- $p=19$: $38,57$.
- $p=23$: $46$; $p=29$: $58$.

**Eliminate the six exceptions.**

- Orders $12,24,48$: simplicity forces $n_2=3$. Conjugation on the three Sylow $2$-subgroups is a nontrivial action. Its kernel is normal; simplicity makes it trivial, embedding $G$ in $S_3$, impossible since $|G|>6$.
- Order $36$: simplicity forces $n_3=4$, giving an embedding $G\hookrightarrow S_4$, impossible since $36\nmid24$.
- Order $30$: simplicity forces $n_5=6$ and $n_3=10$. Distinct prime-order subgroups intersect only at $1$, and elements of orders $3$ and $5$ are disjoint. They would contribute $6\cdot4+10\cdot2=44$ nonidentity elements to a group with only $29$.
- Order $56$: if $n_7=1$, we are done. Otherwise $n_7=8$, yielding $8\cdot6=48$ elements of order $7$. Only eight elements remain, including $1$. Each Sylow $2$-subgroup has eight elements, none of order $7$, so it must be exactly this remaining set. It is therefore unique and normal, again impossible.

Every nonabelian case is excluded. Thus $G$ is abelian, in fact cyclic of prime order.

**Exam strategy:** after routine Sylow counting, the only new tools here are the kernel of the action on Sylow subgroups and disjoint counting for subgroups of prime order.
