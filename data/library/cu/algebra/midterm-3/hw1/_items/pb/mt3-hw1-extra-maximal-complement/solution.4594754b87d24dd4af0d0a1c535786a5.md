**Definitions and results used:** @[The fixed-point congruence for a finite p-group action]mt3-actions; @[Sylow divisibility and congruence; automorphisms permute Sylow subgroups]mt3-sylow; @[Invariant subgroups form intermediate semidirect products]mt3-semidirect; @[Maximal subgroup definition and characteristic subgroup invariance]mt3-foundations; @[The center of a nontrivial finite prime-power group is nontrivial]mt3-pgroups.

**Technique:** Orbit counting produces a P-invariant Sylow subgroup; maximality upgrades every nontrivial invariant subgroup to all of G; apply this again to the characteristic center.

Put $X=G\semid P$. Maximality is proper, so $G\ne1$. If a nontrivial subgroup $A\le G$ is $P$-invariant, then

$$
P<A\semid P\le X,
$$

and maximality forces $A=G$.

**Find an invariant Sylow subgroup.** If $p\mid|G|$, choose $q=p$; then $n_q(G)\equiv1\pmod p$. If $p\nmid|G|$, choose any prime $q\mid|G|$; then $n_q(G)\mid|G|$, so $p\nmid n_q(G)$. In either case $P$ acts on $\Syl_q(G)$, whose cardinality is not divisible by $p$. Its orbits have $p$-power sizes. Reducing the orbit count modulo $p$ shows that at least one orbit has size $1$. Thus some Sylow $q$-subgroup $Q$ is $P$-invariant. Since $Q\ne1$, the first paragraph gives $G=Q$.

**Force abelianity.** Now $G$ is a nontrivial finite $q$-group, so $Z(G)\ne1$. The center is characteristic in $G$, hence preserved by the action of $P$. Apply the same maximality argument with $A=Z(G)$ to obtain $Z(G)=G$.

The key point is that “fixed Sylow subgroup” means preserved **as a subgroup**, not fixed element by element.
