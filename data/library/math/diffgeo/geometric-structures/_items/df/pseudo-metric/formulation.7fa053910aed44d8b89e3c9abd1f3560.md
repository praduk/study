On a @math:diffgeo:manifolds:df:smooth-manifold $M$, a pseudo-Riemannian metric $g$ is a smooth symmetric nondegenerate @[bilinear form]math:algebra:linear-foundations:df:bilinear-forms on every tangent space, with constant signature on each connected component. Its index $s$ is the number of negative squares. A Lorentzian metric here has index one, with signature $(-,+,\ldots,+)$; positive definiteness is the Riemannian case $s=0$.

Nondegeneracy gives inverse bundle maps $\flat:TM\to T^*M$, $X^\flat=g(X,\cdot)$, and $\sharp:T^*M\to TM$. They are called musical isomorphisms. The induced pairing on decomposable $k$-covectors is

$$
\langle\alpha_1\w\cdots\w\alpha_k,\beta_1\w\cdots\w\beta_k\rangle_g
=\det\bigl(g^{-1}(\alpha_i,\beta_j)\bigr).
$$

This pairing is nondegenerate but need not be positive. The @math:diffgeo:connections:th:levi-civita construction extends to this setting: its Koszul proof uses nondegeneracy, smoothness and symmetry, not positivity. Length-minimizing conclusions such as @math:diffgeo:geodesics:th:hopf-rinow do require positivity and do not extend by this observation.
