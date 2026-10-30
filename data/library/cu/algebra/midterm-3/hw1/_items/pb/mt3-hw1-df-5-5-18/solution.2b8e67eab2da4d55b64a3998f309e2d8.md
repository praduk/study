**Definitions and results used:** @[Automorphism group and normality of homomorphism kernels]mt3-foundations; @[External semidirect multiplication, inverses, and its normal factor]mt3-semidirect.

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
