An automorphism preserves element orders: if $x^m=1$, then $\alpha(x)^m=1$, and applying $\alpha^{-1}$ gives the reverse divisibility of orders. The only elements of order $4$ in $D_8$ are $r,r^3$; the other rotations are $1,r^2$, and each reflection $sr^j$ has order $2$. Since $r$ has order $4$, $\alpha(r)$ is either $r$ or $r^3$.

The five involutions of $D_8$ are $r^2,s,sr,sr^2,sr^3$. Although order preservation initially allows five choices for $\alpha(s)$, it cannot be $r^2$. Indeed $\alpha(r)$ already lies in $\langle r\rangle$, and if $\alpha(s)=r^2$ too, the images of the generators would generate a subgroup of $\langle r\rangle$, contradicting surjectivity of $\alpha$. Thus $\alpha(s)$ must be one of the four reflections.

A homomorphism is determined by its values on generators, because its value on every word is then determined. There are at most $2\cdot4=8$ possible pairs $(\alpha(r),\alpha(s))$, so at most eight automorphisms. For this upper bound we need not show that every pair actually works.

**Technique:** use orders to restrict generator images, then use generation/surjectivity to remove choices that preserve orders but cannot yield an automorphism.

**Foundations:** @cu:algebra:midterm-2:definitions:df:automorphism-characteristic, @cu:algebra:midterm-2:theorems:th:inner-characteristic, @cu:algebra:midterm-2:theorems:th:commutator-criterion.
