**Definitions and results used:** @[Derived series]cu:algebra:midterm-3:foundations:df:mt3-derived-series; @[Characteristic terms and functoriality of the three series]cu:algebra:midterm-3:foundations:th:mt3-series-functorial; @[Subgroups, quotients, and extensions of solvable groups]cu:algebra:midterm-3:central:th:mt3-solvable; @[Unique, normal, and characteristic Sylow subgroups]cu:algebra:midterm-3:sylow:th:mt3-sylow-normality; @[Frattini argument: lift conjugacy from a normal subgroup]cu:algebra:midterm-3:sylow:th:mt3-frattini-argument; @[Characteristic subgroups and normality]cu:algebra:midterm-3:foundations:th:mt3-characteristic-normal; @[Subgroup correspondence for a quotient]cu:algebra:midterm-3:foundations:th:mt3-quotient-correspondence.

**Technique:** Induct through an abelian normal subgroup; use Frattini to preserve self-normalization in the quotient.

Induct on $|G|$. If $m=1$, use the trivial subgroup. Suppose $m>1$.

Solvability supplies a nontrivial abelian normal subgroup $A$: take the last nontrivial term of the derived series. If $p\mid|A|$, the unique Sylow $p$-subgroup of the abelian group $A$ is characteristic in $A$, hence normal in $G$. It has order $p$, so it is $P$, contradicting $N_G(P)=P<G$. Thus $p\nmid|A|$.

In $\overline G=G/A$, put $\overline P=PA/A$. This is a Sylow $p$-subgroup. To show it is self-normalizing, let $M$ be the inverse image of $N_{\overline G}(\overline P)$. Then $PA\nsubg M$, and Frattini's argument gives

$$
M=PA\,N_M(P)=PA,
$$

because $N_M(P)\le N_G(P)=P$. Consequently $N_{\overline G}(\overline P)=\overline P$.

The smaller solvable group $\overline G$ therefore has, by induction, a normal subgroup $\overline H$ of order $m/|A|$. Its inverse image $H$ is normal in $G$ and has order $m$.

**Where solvability enters:** it supplies $A\ne1$ abelian and ensures $G/A$ is solvable. Notice that the hypothesis is $|G|=pm$, with only one factor of $p$.
