**Definitions and results used:** @[Sylow theorem]cu:algebra:midterm-3:sylow:th:mt3-sylow; @[Unique, normal, and characteristic Sylow subgroups]cu:algebra:midterm-3:sylow:th:mt3-sylow-normality; @[Priority: the corollary and the normalizer it produces]cu:algebra:midterm-3:sylow:th:mt3-intersection; @[Every index-two subgroup is normal]cu:algebra:midterm-3:foundations:th:mt3-index-two; @[Normalizer]cu:algebra:midterm-3:foundations:df:mt3-normalizer; @[Lagrange’s theorem and the index formula]cu:algebra:midterm-3:foundations:th:mt3-lagrange; @[Finite p-groups are nilpotent]cu:algebra:midterm-3:sylow:th:mt3-pgroup-nilpotent; @[Every nilpotent group is solvable]cu:algebra:midterm-3:central:th:mt3-nilpotent-solvable; @[Subgroups, quotients, and extensions of solvable groups]cu:algebra:midterm-3:central:th:mt3-solvable.

**(a).** $96=2^5\cdot3$; $n_2\mid3$ and $n_2\equiv1\pmod2$, so $n_2=1$ or3. If 1, the subgroup $P$ of order 32 is normal.

**(b).** $3\not\equiv1\pmod4$. The $(N)^+$ corollary gives $[P:H]=[Q:H]=2$. Since $|P|=|Q|=32$, $|H|=16$.

**(c).** An index 2 subgroup is normal, so $H\trianglelefteq P,Q$ and $P,Q\le N_G(H)$. As $P\ne Q$, this normalizer strictly contains $P$. Its order divides 96 and is a multiple of 32 larger than 32; the only possibility is96. Thus $N_G(H)=G$, i.e. $H\trianglelefteq G$.

**(d).** If $n_2=1$, then $P$ is a solvable 2-group and $G/P$ has order 3 and is cyclic. If $n_2=3$, then $H$ is a solvable 2-group and $G/H$ has order 6. Any order 6 group has a normal Sylow-3 subgroup with quotient of order 2, so is solvable. In both cases the extension criterion makes $G$ solvable, and the exhibited proper nontrivial normal subgroup proves nonsimplicity.

**Self-check:** did you explicitly verify the modulus 4, both indices 2, normality inside $P,Q$, and the divisors available to the normalizer? Those are the links in the argument.
