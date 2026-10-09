Because $G$ is finite, among the proper subgroups containing $H$ choose one, $M$, of largest order. Any proper subgroup strictly containing $M$ would have larger order, so $M$ is maximal. Each conjugate of $H$ lies inside the corresponding conjugate of $M$. It is enough to show the conjugates of $M$ do not cover $G$.

If $M\nsubg G$, every conjugate of $M$ is $M$, and their union is the proper subgroup $M$.

If $M$ is not normal, put $t=[G:M]$. Since $M<G$, $t\ge2$. Exercise 4.3.23 bounds the number of nonidentity elements in the union by $(|M|-1)t$. Adding the common identity gives

$$
\left|\bigcup_{g\in G}gMg^{-1}\right|\le1+(|M|-1)t=|G|-t+1<|G|.
$$

Therefore this union is proper, and so is the union of conjugates of $H$.

**Technique:** enlarge to a maximal subgroup to count conjugates exactly, then exploit the fact that all conjugates share the identity. Finiteness is essential to this counting proof.

**Foundations:** @cu:algebra:midterm-2:theorems:th:orbit-stabilizer, @cu:algebra:midterm-2:definitions:df:normalizer-centralizer.
