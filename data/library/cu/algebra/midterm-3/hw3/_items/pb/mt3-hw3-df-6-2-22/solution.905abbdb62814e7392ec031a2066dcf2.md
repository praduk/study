**Definitions and results used:** @[Strict normalizer growth in finite p-groups]cu:algebra:midterm-3:sylow:th:mt3-pgroup-normalizer; @[Sylow theorem]cu:algebra:midterm-3:sylow:th:mt3-sylow; @[Normalizer]cu:algebra:midterm-3:foundations:df:mt3-normalizer.

**Technique:** Assume the normalizer is a p-group and place it inside one Sylow subgroup; maximality forces two distinct Sylow groups to be equal.

Suppose $N_G(D)$ were a $p$-group, and place it in a Sylow $p$-subgroup $T$ of $G$. Strict normalizer growth gives

$$
D<N_P(D)\le P\cap T.
$$

If $T\ne P$, this contradicts maximality of $|D|$; hence $T=P$. Applying the same argument to $R$ gives $T=R$, contradicting $P\ne R$. Therefore $N_G(D)$ is not a $p$-group.

This is the key first conclusion of exercise 6.2.13, with a shorter direct proof. It also covers $D=1$: then $N_G(D)=G$.
