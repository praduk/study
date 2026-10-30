**Definitions and results used:** @[lower central series and preservation of commutators]mt3-series; @[equivalence of upper and lower nilpotence criteria]mt3-nilpotent; @[normal subgroups, quotient maps, and centers]mt3-foundations.

**Technique:** Pass commutators through inclusion and surjection; use S₃ as the standard extension counterexample.

Use $\gamma_1(G)=G$, $\gamma_{i+1}(G)=[\gamma_i(G),G]$. Nilpotence of class at most $c$ is equivalent to $\gamma_{c+1}(G)=1$.

For $H\le G$, induction gives $\gamma_i(H)\le\gamma_i(G)$, since commutators of elements of smaller subgroups are also commutators in the larger ones. Thus $\gamma_{c+1}(H)=1$.

For a surjection $\pi:G\to G/N$, induction and preservation of commutators give $\gamma_i(G/N)=\pi(\gamma_i(G))$. Thus $\gamma_{c+1}(G/N)=1$. Neither argument uses finiteness.

For failure under extensions, take $G=S_3$ and $H=A_3$. Both $H\cong C_3$ and $G/H\cong C_2$ are abelian, hence nilpotent. But $Z(S_3)=1$, so its upper central series stays $1$ and never reaches $S_3$.
