**Definitions and results used:** @[solvable subgroup closure and termination of the derived series]mt3-solvable; @[minimal normality, characteristic-in-normal, and Cauchy’s theorem]mt3-foundations; @[abelian primary components and the power map]mt3-abelian; @[elementary abelian p-groups]mt3-linear.

**Technique:** Apply minimal normality successively to M′, a primary component, and Mᵖ.

The subgroup $M$ is solvable because it lies in $G$. Its derived subgroup $M'$ is characteristic in $M$, hence normal in $G$. Minimality says $M'=1$ or $M$. The second possibility would make every derived term of $M$ equal $M\ne1$, contradicting solvability. Thus $M$ is abelian.

Choose a prime $p\mid|M|$. The subgroup of all elements of $p$-power order in the finite abelian group $M$ is nontrivial and characteristic in $M$, hence normal in $G$. Minimality forces it to be all of $M$, so $M$ is a $p$-group. The power map $m\mapsto m^p$ has a nontrivial kernel by Cauchy's theorem, so its image $M^p$ is proper. This image is characteristic in $M$, hence normal in $G$, so minimality forces $M^p=1$. Therefore $M$ is abelian of exponent $p$, that is, $M\cong C_p^r$ for some $r\ge1$.
