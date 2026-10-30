**Definitions and results used:** @[Fixed-point congruence for p-group actions]cu:algebra:midterm-3:foundations:th:mt3-fixed-points; @[Sylow theorem]cu:algebra:midterm-3:sylow:th:mt3-sylow; @[Semidirect product construction and internal recognition]cu:algebra:midterm-3:semidirect:th:mt3-semidirect-recognition; @[Maximal subgroup]cu:algebra:midterm-3:foundations:df:mt3-maximal-subgroup; @[Characteristic subgroup]cu:algebra:midterm-3:foundations:df:mt3-characteristic; @[Center of a group]cu:algebra:midterm-3:foundations:df:mt3-center; @[A nontrivial finite p-group has nontrivial center]cu:algebra:midterm-3:sylow:th:mt3-pgroups.

**Technique:** Orbit counting produces a P-invariant Sylow subgroup; maximality upgrades every nontrivial invariant subgroup to all of G; apply this again to the characteristic center.

Put $X=G\semid P$. Maximality is proper, so $G\ne1$. If a nontrivial subgroup $A\le G$ is $P$-invariant, then

$$
P<A\semid P\le X,
$$

and maximality forces $A=G$.

**Find an invariant Sylow subgroup.** If $p\mid|G|$, choose $q=p$; then $n_q(G)\equiv1\pmod p$. If $p\nmid|G|$, choose any prime $q\mid|G|$; then $n_q(G)\mid|G|$, so $p\nmid n_q(G)$. In either case $P$ acts on $\Syl_q(G)$, whose cardinality is not divisible by $p$. Its orbits have $p$-power sizes. Reducing the orbit count modulo $p$ shows that at least one orbit has size $1$. Thus some Sylow $q$-subgroup $Q$ is $P$-invariant. Since $Q\ne1$, the first paragraph gives $G=Q$.

**Force abelianity.** Now $G$ is a nontrivial finite $q$-group, so $Z(G)\ne1$. The center is characteristic in $G$, hence preserved by the action of $P$. Apply the same maximality argument with $A=Z(G)$ to obtain $Z(G)=G$.

The key point is that “fixed Sylow subgroup” means preserved **as a subgroup**, not fixed element by element.
