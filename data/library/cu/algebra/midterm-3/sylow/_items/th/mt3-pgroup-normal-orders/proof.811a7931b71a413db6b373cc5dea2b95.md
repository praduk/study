**Definitions and results used:** @[A nontrivial normal subgroup meets the center]mt3-pgroups; @[Cauchy theorem]mt3-cauchy; @[Quotient correspondence]mt3-quotient-correspondence.

Induct on $|P|$. For $b=0$, choose $H=1$. For $b\ge1$, $N$ is nontrivial, so $N\cap Z(P)$ contains an element of order $p$ by the center theorem and Cauchy. Its subgroup $C$ is central and normal in $P$.

Apply induction to the smaller group $P/C$ and its normal subgroup $N/C$ of order $p^{m-1}$. There is a subgroup $\overline H\trianglelefteq P/C$ inside $N/C$ of order $p^{b-1}$. Its full preimage $H$ is normal in $P$, lies in $N$, and has order $p\cdot p^{b-1}=p^b$.
