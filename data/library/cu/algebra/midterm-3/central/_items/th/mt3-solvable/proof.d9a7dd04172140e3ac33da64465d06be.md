**Definitions and results used:** @[Derived series and commutator preservation]mt3-series; @[Characteristic-in-normal, minimal normal subgroups, and Cauchy]mt3-foundations; @[Elementary abelian groups]mt3-linear.

Commutator preservation proves subgroup and quotient closure. If $G/N$ has derived length $a$, then $G^{(a)}\le N$; if $N$ has length $b$, then $G^{(a+b)}\le N^{(b)}=1$. This is the extension argument. The abelian-factor series characterization follows by comparing any such series to the derived series, whose factors are themselves abelian.

Since $G^{(i)}\le L_i(G)$ inductively, nilpotence implies solvability. For simple solvable $G$, the characteristic subgroup $G'$ cannot equal $G$ (or the derived series never decreases), so $G'=1$ and $G$ is abelian simple, hence cyclic of prime order.

Let $M$ be minimal normal in finite solvable $G$. Its characteristic subgroup $M'$ is normal in $G$, and solvability prevents $M'=M\ne1$; so $M'=1$. Thus $M$ is abelian. Each of its Sylow subgroups is characteristic, forcing a single prime $p$. The characteristic subgroup $M^p=\{x^p:x\in M\}$ is proper because the power map has nontrivial kernel by Cauchy; minimal normality forces $M^p=1$. Hence $M\cong C_p^r$.
