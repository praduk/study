**Definitions and results used:** @[Complement to a normal subgroup]cu:algebra:midterm-3:semidirect:df:mt3-complement; @[Semidirect product construction and internal recognition]cu:algebra:midterm-3:semidirect:th:mt3-semidirect-recognition; @[A nontrivial finite p-group has nontrivial center]cu:algebra:midterm-3:sylow:th:mt3-pgroups; @[Center of a group]cu:algebra:midterm-3:foundations:df:mt3-center; @[Lagrange’s theorem and the index formula]cu:algebra:midterm-3:foundations:th:mt3-lagrange.

**Technique:** A central semidirect factor makes the product direct; the other p-group factor contributes an unavoidable center.

Suppose such $H$ exists. Since $Z(G)$ is central, it commutes with $H$, so this would actually be an internal direct product. Also $H\ne1$, since otherwise $G=Z(G)$ would be abelian.

The nontrivial finite $p$-group $H$ has $Z(H)\ne1$. Every element of $Z(H)$ commutes with $H$ and with $Z(G)$; because $G=HZ(G)$, it commutes with all of $G$. Therefore

$$
1\ne Z(H)\le H\cap Z(G)=1,
$$

a contradiction.
