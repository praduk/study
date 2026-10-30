**Definitions and results used:** @[Sylow subgroups]mt3-sylow-subgroup; @[Class equation]mt3-class-equation; @[Cauchy theorem]mt3-cauchy; @[Quotient correspondence]mt3-quotient-correspondence; @[Fixed-point congruence]mt3-fixed-points; @[Subgroup products]mt3-subgroup-product.

**Existence.** Induct on $|G|$. If $a=0$, take the trivial subgroup. If a proper subgroup has order divisible by $p^a$, apply induction in it. Otherwise every proper subgroup has a smaller $p$-part. For any noncentral $x$, the proper subgroup $C_G(x)$ therefore has index divisible by $p$. The class equation then implies $p\mid|Z(G)|$. By Cauchy, $Z(G)$ contains a subgroup $C$ of order $p$, normal because it is central. By induction $G/C$ has a Sylow subgroup of order $p^{a-1}$; its full preimage has order $p^a$.

**Containment and conjugacy.** Fix $P$ of order $p^a$ and let any $p$-subgroup $Q$ act by left multiplication on $G/P$. This coset set has size $m$, not divisible by $p$, so the fixed-point congruence gives a fixed coset $gP$. Then $g^{-1}Qg\le P$. If $Q$ is Sylow, the two groups have the same order and the inclusion is equality.

**Counting.** Conjugation by $G$ on its Sylow subgroups is transitive, with stabilizer $N_G(P)$. Orbit–stabilizer gives $n_p=[G:N_G(P)]$, and $P\le N_G(P)$ gives $n_p\mid m$.

Finally let $P$ act by conjugation on $\Syl_p(G)$. If it fixes $Q$, then $P\le N_G(Q)$, so $QP$ is a $p$-subgroup containing $Q$. Its order cannot exceed $p^a$, hence $QP=Q$ and $P=Q$. Thus exactly one Sylow subgroup is fixed. The fixed-point congruence gives $n_p\equiv1\pmod p$.

This is the elementary class-equation proof of existence followed by the coset-action proof of containment; compare Dummit–Foote §4.5, Theorem18, printed pp.139–141.
