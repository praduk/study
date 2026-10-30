**Definitions and results used:** @[Sylow theorem]cu:algebra:midterm-3:sylow:th:mt3-sylow; @[Unique, normal, and characteristic Sylow subgroups]cu:algebra:midterm-3:sylow:th:mt3-sylow-normality; @[Counting distinct prime-order subgroups]cu:algebra:midterm-3:sylow:th:mt3-prime-order-intersections; @[Lagrange’s theorem and the index formula]cu:algebra:midterm-3:foundations:th:mt3-lagrange.

**Technique:** Assume two largest-prime Sylows are nonnormal and count disjoint prime-order elements.

In fact a Sylow $q$- or $r$-subgroup is normal. Suppose both are nonnormal. Since $n_r\mid pq$ and $n_r\equiv1\pmod r$, with $p,q<r$, we must have $n_r=pq$. Since $n_q\mid pr$ and $n_q\ne1$, the congruence excludes $p$, so $n_q=r$ or $pr$ and in particular $n_q\ge r$.

Distinct subgroups of a given prime order share only $1$, and elements of orders $q$ and $r$ are distinct. Thus the number of nonidentity elements is at least

$$
pq(r-1)+r(q-1)=pqr+\bigl(r(q-1)-pq\bigr)>pqr.
$$

The final inequality follows from $q-1\ge p$ and $r>q$. This is impossible.
