**(a)** The identity belongs to both $H$ and $K$. If $a,b\in H\cap K$, then $ab^{-1}$ belongs to $H$ and also to $K$, so $H\cap K$ is a subgroup by the one-step subgroup test. For $g\in G$ and $a\in H\cap K$, normality of each subgroup gives $gag^{-1}\in H$ and $gag^{-1}\in K$. Hence $g(H\cap K)g^{-1}\subseteq H\cap K$. Applying the same inclusion to $g^{-1}$ yields the reverse inclusion after conjugating by $g$. Thus equality holds for every $g$.

**(b)** Let $(N_i)_{i\in I}$ be a family with $I\ne\varnothing$, and put $N=\bigcap_{i\in I}N_i$. We use the quantifier “for every $i\in I$,” not an enumeration. The identity lies in every $N_i$. If $a,b\in N$, then for every $i$, $a,b\in N_i$, so $ab^{-1}\in N_i$. Therefore $ab^{-1}\in N$. Similarly, if $a\in N$ and $g\in G$, then $gag^{-1}\in N_i$ for every $i$, so $gag^{-1}\in N$. The argument with $g^{-1}$ again upgrades inclusion to equality. Hence $N\nsubg G$.

**Technique:** prove a property in each member of the family, then put back the universal quantifier. No finiteness or countability is used.

**Foundations:** @cu:algebra:midterm-2:definitions:df:normal-quotient, @cu:algebra:midterm-2:theorems:th:commutator-criterion.
