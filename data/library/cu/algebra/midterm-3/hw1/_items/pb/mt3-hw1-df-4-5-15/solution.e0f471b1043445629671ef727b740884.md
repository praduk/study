**Definitions and results used:** @[Sylow counts, Sylow subgroup order, and uniqueness iff normal]mt3-sylow; @[Lagrange theorem and orders of subgroup elements]mt3-foundations; @[Distinct prime-order subgroups intersect trivially]mt3-sylow.

**Technique:** When the largest-prime Sylow count is maximal, count its nonidentity elements and inspect the remaining capacity.

Since $351=3^3\cdot13$, Sylow gives $n_{13}=1$ or $27$. The first case is finished. In the second case, distinct order-$13$ subgroups meet only in $1$, so they contain $27(13-1)=324$ distinct nonidentity elements. Exactly $27$ elements remain, including $1$. Every Sylow $3$-subgroup has $27$ elements and contains none of those order-$13$ elements, so it must equal the entire remaining set. Hence it is unique and normal.
