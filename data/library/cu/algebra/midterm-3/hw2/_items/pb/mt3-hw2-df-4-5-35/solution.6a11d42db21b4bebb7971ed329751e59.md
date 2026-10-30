**Definitions and results used:** @[Sylow existence, containment, and maximal order]mt3-sylow; @[conjugation, intersections, and subgroup order]mt3-foundations.

**Technique:** Start with a Sylow subgroup of H, embed it in a conjugate of P, then squeeze the intersection.

Choose $Q\in\Syl_p(H)$. Sylow containment in $G$ gives $Q\le gPg^{-1}$ for some $g\in G$. Then

$$
Q\le gPg^{-1}\cap H\le H.
$$

The middle group is a $p$-group, so maximality of the order of $Q$ gives equality.

For the warning, take $G=S_3$, $P=\langle(12)\rangle$, and $H=\langle(23)\rangle$. Here $P\cap H=1$, and for every $h\in H$,

$$
hPh^{-1}\cap H=h(P\cap H)h^{-1}=1.
$$

This is not Sylow in $H$, whose order is $2$. A conjugator from all of $G$ can send $(12)$ to $(23)$, as required by the first part.
