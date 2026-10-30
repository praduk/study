**Definitions and results used:** @[Sylow number restrictions, uniqueness, and prime-order element counting]mt3-sylow; @[Simple groups and Lagrange's theorem]mt3-foundations.

**Technique:** Count elements of prime order; if the remainder has exactly the order of another Sylow subgroup, that Sylow subgroup is unique.

Assume $G$ is simple. For every prime divisor $p$, its Sylow number $n_p$ must exceed $1$.

- $80=2^4\cdot5$: Sylow gives $n_5=16$. The $16$ subgroups of order $5$ contribute $16(5-1)=64$ nonidentity elements. Only $16$ elements remain, including $1$. Every Sylow $2$-subgroup has order $16$ and lies in that remainder, so there is exactly one: contradiction.
- $351=3^3\cdot13$: $n_{13}=27$. Its $27\cdot12=324$ elements of order $13$ leave $27$ elements, forcing the Sylow $3$-subgroup to be unique.
- $3875=5^3\cdot31$: $n_{31}=125$. Its $125\cdot30=3750$ elements of order $31$ leave $125$ elements, forcing the Sylow $5$-subgroup to be unique.
- $5313=3\cdot7\cdot11\cdot23$: Sylow gives $n_7=253$ and $n_{23}=231$. These already contribute $253\cdot6+231\cdot22=6600>5313$ distinct elements: contradiction.

The counting formula $n_p(p-1)$ is valid here because these Sylow subgroups have **prime order**; their pairwise intersections are trivial.
