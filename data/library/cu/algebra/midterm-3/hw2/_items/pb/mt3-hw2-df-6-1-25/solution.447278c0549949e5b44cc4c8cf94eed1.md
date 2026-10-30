**Definitions and results used:** @[Frattini subgroup and nongenerators]cu:algebra:midterm-3:advanced:df:mt3-frattini-subgroup; @[Maximal subgroup]cu:algebra:midterm-3:foundations:df:mt3-maximal-subgroup; @[Characteristic subgroups and normality]cu:algebra:midterm-3:foundations:th:mt3-characteristic-normal; @[Frattini argument: lift conjugacy from a normal subgroup]cu:algebra:midterm-3:sylow:th:mt3-frattini-argument; @[Equivalent criteria for finite nilpotent groups]cu:algebra:midterm-3:central:th:mt3-nilpotent; @[Normalizer]cu:algebra:midterm-3:foundations:df:mt3-normalizer.

**Technique:** Frattini argument gives G = Φ(G)N_G(P); a proper normalizer would lie in a maximal subgroup already containing Φ(G).

Automorphisms permute the maximal subgroups of $G$, so $F=\Phi(G)$ is characteristic and hence normal in $G$. If $F=1$, the conclusion is immediate. For any prime $p\mid|F|$, choose $P\in\Syl_p(F)$. Frattini's argument gives $G=F N_G(P)$.

If $N_G(P)<G$, finiteness puts it in a maximal subgroup $M$. Since $F\le M$ by definition, the equality $G=F N_G(P)$ would imply $G\le M$, a contradiction. Thus $N_G(P)=G$ and $P\nsubg G$. In particular every Sylow subgroup of $F$ is normal in $F$, so the finite nilpotence criterion proves $F$ nilpotent.
