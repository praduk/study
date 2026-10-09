Suppose $Z(G)\ne1$. By Lagrange, its order divides $pq$, so it is $p,q$, or $pq$ (when $p=q$, the distinct possibilities are $p,p^2$).

If $|Z(G)|=pq$, then $Z(G)=G$, which is the definition of $G$ being abelian. Otherwise $G/Z(G)$ has prime order: its order is $q$ when $|Z(G)|=p$, or $p$ when $|Z(G)|=q$. A group of prime order is cyclic, since any nonidentity element generates a nontrivial subgroup whose order divides that prime. Exercise 3.1.36 now gives that $G$ is abelian.

Thus a nontrivial center forces $G$ abelian. Equivalently, if $G$ is not abelian, its center must be trivial.

**Technique:** constrain the order of the center, then inspect the central quotient. This alone does not assert that a nonabelian group of order $pq$ exists.

**Foundations:** @cu:algebra:midterm-2:theorems:th:cosets-lagrange, @cu:algebra:midterm-2:theorems:th:first-isomorphism, @cu:algebra:midterm-2:theorems:th:orbit-stabilizer.
