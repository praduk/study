Let $H\le G$ have index $p$. Left multiplication on the $p$ left cosets defines a homomorphism $\varphi:G\to S_p$. Let $K=\ker\varphi$. An element of $K$ fixes the coset $H$, so it belongs to $H$; hence $K\le H$.

By the First Isomorphism Theorem the image has order $[G:K]$, which is a power of $p$ because $|G|=p^a$. It divides $p!$ because it is a subgroup of $S_p$. There is only one factor divisible by $p$ in the list $1,2,\ldots,p$, so the highest power of $p$ dividing $p!$ is $p$ itself. Thus $[G:K]\le p$. But

$$
[G:K]=[G:H][H:K]=p[H:K]\ge p.
$$

Therefore $[H:K]=1$, so $H=K$. A kernel is normal, proving the claim.

If $|G|=p^2$, Cauchy's theorem supplies an element of order $p$. Its cyclic subgroup has order $p$ and index $p$, so it is normal by the first part.

**Technique:** a small coset action restricts the order of an image. Compare that bound with the index forced by $K\le H$. This is the same argument as the lecture's smallest-prime-index theorem.

**Foundations:** @cu:algebra:midterm-2:theorems:th:coset-action, @cu:algebra:midterm-2:theorems:th:first-isomorphism.
