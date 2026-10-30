**Definitions and results used:** @[Automorphisms, inner automorphisms, and outer automorphisms]cu:algebra:midterm-3:foundations:df:mt3-automorphism; @[Homomorphism, kernel, and image]cu:algebra:midterm-3:foundations:df:mt3-homomorphism; @[External semidirect product]cu:algebra:midterm-3:semidirect:df:mt3-semidirect; @[Semidirect product construction and internal recognition]cu:algebra:midterm-3:semidirect:th:mt3-semidirect-recognition.

**Technique:** If the desired conjugations are prescribed automorphisms, adjoin the automorphism group as a semidirect factor.

Use the natural action of $\Aut(H)$ on $H$ and form the **holomorph**

$$
G=H\semid\Aut(H),\qquad (h,\alpha)(k,\beta)=(h\alpha(k),\alpha\beta).
$$

Identify $H$ with $H\times\{\id\}$, which is the kernel of the projection $G\to\Aut(H)$ and hence normal. For any $\alpha\in\Aut(H)$, take $g=(1,\alpha)$. Then

$$
g(h,\id)g^{-1}=(\alpha(h),\id).
$$

Thus conjugation by $g$ restricts to $\alpha$ on $H$. This works for finite or infinite $H$.
