**Definitions and results used:** @[Upper and lower central series; commutators under quotients]mt3-series; @[Nilpotence of finite p-groups]mt3-pgroups; @[Unique Sylow subgroups are characteristic]mt3-sylow; @[Frattini factorization]mt3-frattini-argument.

For the central-series equivalence, induct on $c$. If $Z_c(G)=G$, the quotient by $Z(G)$ has class at most $c-1$, so $L_{c-1}(G)\le Z(G)$ and $L_c(G)=1$. Conversely, $L_c(G)=1$ implies $L_{c-1}(G)\le Z(G)$, so the quotient has lower term $c-1$ trivial; induction makes its upper term $c-1$ the whole quotient, hence $Z_c(G)=G$. The case $c=0$ is $G=1$. Commutators descend under surjections, as required in both directions.

For a nilpotent group, choose the least $i$ with $Z_i(G)\nleq H$ for a proper subgroup $H$. An element of $Z_i(G)\setminus H$ normalizes $H$ because its commutators with $H$ lie in $Z_{i-1}(G)\le H$. This proves strict normalizer growth.

In a finite group satisfying strict normalizer growth, put $N=N_G(P)$ for Sylow $P$. Since $P$ is the unique Sylow $p$-subgroup of $N$, it is characteristic there. Every element normalizing $N$ therefore normalizes $P$, so $N_G(N)=N$. Strict growth forces $N=G$, hence $P\trianglelefteq G$. Distinct normal Sylow factors have trivial intersection and commute; their product has full order, giving the direct product. Conversely each Sylow factor is nilpotent, and the center of a direct product is the product of the centers, so the product is nilpotent.

Strict growth makes maximal subgroups normal. Conversely, if all maximal subgroups are normal and $N_G(P)<G$, choose a maximal $M$ containing it. Frattini's argument applied to $M\trianglelefteq G$ gives $G=M N_G(P)=M$, contradiction (here $P$ is Sylow in $M$).

Subgroup and quotient closure follow from the lower-series inclusions/equalities in @mt3-series. The same quotient argument gives $G/Z(G)$ nilpotent ⇒ $G$ nilpotent.
