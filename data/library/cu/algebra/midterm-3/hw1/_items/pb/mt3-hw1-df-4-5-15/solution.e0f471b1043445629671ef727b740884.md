**Definitions and results used:** @[Sylow theorem]cu:algebra:midterm-3:sylow:th:mt3-sylow; @[Unique, normal, and characteristic Sylow subgroups]cu:algebra:midterm-3:sylow:th:mt3-sylow-normality; @[Counting distinct prime-order subgroups]cu:algebra:midterm-3:sylow:th:mt3-prime-order-intersections; @[Lagrange’s theorem and the index formula]cu:algebra:midterm-3:foundations:th:mt3-lagrange.

**Technique:** When the largest-prime Sylow count is maximal, count its nonidentity elements and inspect the remaining capacity.

Since $351=3^3\cdot13$, Sylow gives $n_{13}=1$ or $27$. The first case is finished. In the second case, distinct order-$13$ subgroups meet only in $1$, so they contain $27(13-1)=324$ distinct nonidentity elements. Exactly $27$ elements remain, including $1$. Every Sylow $3$-subgroup has $27$ elements and contains none of those order-$13$ elements, so it must equal the entire remaining set. Hence it is unique and normal.
