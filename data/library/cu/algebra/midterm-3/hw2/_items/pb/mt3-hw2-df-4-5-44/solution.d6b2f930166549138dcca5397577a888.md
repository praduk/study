**Definitions and results used:** @[Normalizer–centralizer theorem]cu:algebra:midterm-3:foundations:th:mt3-normalizer-centralizer; @[Automorphisms of a finite cyclic group]cu:algebra:midterm-3:foundations:th:mt3-cyclic-automorphisms; @[Sylow p-subgroup]cu:algebra:midterm-3:sylow:df:mt3-sylow-subgroup; @[Lagrange’s theorem and the index formula]cu:algebra:midterm-3:foundations:th:mt3-lagrange.

**Technique:** Use N/C ↪ Aut(P), remove the p-part using P ≤ C, and compare prime divisors.

Write $|P|=p^a$, $N=N_G(P)$, and $C=C_G(P)$. Conjugation embeds $N/C$ into $\Aut(P)$, whose order is $p^{a-1}(p-1)$. Since $P$ is abelian, $P\le C\le N$. As $P$ is Sylow in $N$, the index $[N:C]$ is prime to $p$. Consequently $[N:C]\mid(p-1)$. But $[N:C]$ also divides $|G|$, and every prime divisor of $|G|$ is at least $p$. No integer greater than $1$ can satisfy both conditions. Thus $[N:C]=1$.

**Trap:** this concludes equality of the normalizer and centralizer, not that either equals all of $G$.
