First $A\cap B\nsubg G$, because conjugation preserves each of $A$ and $B$ and hence their intersection.

For arbitrary $x,y\in G$, commutativity in $G/A$ gives

$$
x^{-1}y^{-1}xy\in A.
$$

The same argument in $G/B$ gives $x^{-1}y^{-1}xy\in B$. Therefore every commutator lies in $A\cap B$. In the quotient by this intersection, for arbitrary cosets $\bar x,\bar y$, this says

$$
\bar x^{-1}\bar y^{-1}\bar x\bar y=1,
$$

which is equivalent to $\bar x\bar y=\bar y\bar x$. All quotient elements commute, so the quotient is abelian.

**Equivalent concise view.** The commutator criterion says $G'\le A$ and $G'\le B$, hence $G'\le A\cap B$. The same criterion then gives the conclusion. The element calculation above explains every step of that shorthand.

**Technique:** express both assumptions as membership of the same element, then intersect. There is no need to assume $G=AB$ or use a direct-product isomorphism.

**Foundations:** @cu:algebra:midterm-2:theorems:th:commutator-criterion.
