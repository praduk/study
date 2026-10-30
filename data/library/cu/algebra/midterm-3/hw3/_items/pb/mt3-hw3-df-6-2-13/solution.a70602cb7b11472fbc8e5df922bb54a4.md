**Definitions and results used:** @[Strict normalizer growth in a finite p-group]mt3-pgroups; @[Sylow containment and containment of normal p-subgroups]mt3-sylow; @[Normalizer definition and subgroup-order divisibility]mt3-foundations.

**Technique:** Maximize an intersection, use strict normalizer growth, and turn any larger intersection into a contradiction.

Put $N=N_G(D)$. The normalizer condition in a finite $p$-group gives

$$
D<N_P(D),\qquad D<N_Q(D).
$$

Choose Sylow $p$-subgroups $S,T$ of $N$ containing these two normalizers. If $S=T$, place $S$ in a Sylow $p$-subgroup $U$ of $G$. Then $|U\cap P|>|D|$ forces $U=P$ by the maximal choice of $D$; likewise $U=Q$, a contradiction. Hence $N$ has at least two Sylow $p$-subgroups.

Now take any distinct $S,T\in\Syl_p(N)$ and choose $U,V\in\Syl_p(G)$ containing them. Because $D$ is a normal $p$-subgroup of $N$, it lies in both $S$ and $T$. If $U=V$, then the $p$-subgroup $N_U(D)$ contains both $S$ and $T$, forcing $S=T$. Thus $U\ne V$, and maximality gives

$$
D\le S\cap T\le U\cap V,\qquad |U\cap V|\le|D|.
$$

Therefore $S\cap T=D$.

Since $D<S$, $p|D|$ divides $|N|$. Since $N$ has multiple Sylow $p$-subgroups, it is not a $p$-group; consequently some prime other than $p$ also divides $|N|$. Do not assume $S,T$ are Sylow in $G$.
