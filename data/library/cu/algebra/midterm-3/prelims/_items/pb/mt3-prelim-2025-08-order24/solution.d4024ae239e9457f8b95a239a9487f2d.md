**Technique trigger:** very few Sylow $2$-subgroups → check their number modulo $4$ → find a large intersection → force its normalizer to be the whole group.

**Definitions and results used:** @[Normalizer]cu:algebra:midterm-3:foundations:df:mt3-normalizer and @[Lagrange's theorem]cu:algebra:midterm-3:foundations:th:mt3-lagrange; @[Sylow numbers]cu:algebra:midterm-3:sylow:th:mt3-sylow and @[unique Sylow subgroups are normal]cu:algebra:midterm-3:sylow:th:mt3-sylow-normality; @[The Sylow (N)+ corollary]cu:algebra:midterm-3:sylow:th:mt3-intersection and @[index-two subgroups are normal]cu:algebra:midterm-3:foundations:th:mt3-index-two.

Since $24=2^3\cdot3$, a Sylow $2$-subgroup has order $8$, and Sylow gives

$$
n_2\mid3,\qquad n_2\equiv1\pmod2.
$$

Thus $n_2=1$ or $3$.

If $n_2=1$, the unique Sylow $2$-subgroup is normal and has order $8$, as required.

Suppose $n_2=3$. Now $3\not\equiv1\pmod4$. Apply the corollary with $p=2$: there are distinct $P,Q\in\Syl_2(G)$ for which $D=P\cap Q$ has index $2$ in both. Therefore $|D|=8/2=4$.

Index-two normality gives $D\trianglelefteq P$ and $D\trianglelefteq Q$, so

$$
P,Q\le N_G(D).
$$

The normalizer contains $P$ and also the distinct subgroup $Q$ of the same order. Hence it strictly contains $P$, so its order is a multiple of $8$ greater than $8$. By Lagrange it divides $24$; the only possibility is $|N_G(D)|=24$. Thus $N_G(D)=G$, meaning $D\trianglelefteq G$. This gives the required normal subgroup of order $4$.

**Check the decisive step:** the corollary gives normality in $P$ and $Q$. The order argument is what upgrades this to normality in $G$.
