Suppose $G$ has distinct Sylow $p$-subgroups. Choose $P\ne Q$ so that $H=P\cap Q$ has maximum possible order. Then $N=N_G(H)$ has at least two Sylow $p$-subgroups, and any two distinct ones intersect exactly in $H$. In particular **$N$ is not a $p$-group** and $p|H|$ divides $|N|$.

**Second strategy:** given an order-$q$ subgroup $Q\trianglelefteq N$, use $N/C_N(Q)\hookrightarrow\Aut(C_q)$, whose order is $q-1$. This often forces a Sylow $p$-subgroup of $N$ to centralize $Q$. Then reverse roles: $Q\le C_G(P)\le N_G(P)$; compare the known order of $N_G(P)$. See HW3 §6.2.7,10,12.

Prerequisites: @[Normalizer]cu:algebra:midterm-3:foundations:df:mt3-normalizer, @[Sylow theorem]cu:algebra:midterm-3:sylow:th:mt3-sylow, @[A normal p-subgroup lies in every Sylow p-subgroup]cu:algebra:midterm-3:sylow:th:mt3-normal-p-subgroup, and @[Strict normalizer growth in finite p-groups]cu:algebra:midterm-3:sylow:th:mt3-pgroup-normalizer.
