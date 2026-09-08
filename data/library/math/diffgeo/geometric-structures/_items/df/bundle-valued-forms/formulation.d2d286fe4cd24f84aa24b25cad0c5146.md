For a smooth vector bundle $E\to M$, let $\Gamma(E)$ denote its smooth sections. An $E$-valued $k$-form is a section of $\Lambda^kT^*M\otimes E$; the space of these sections is $\Omega^k(M;E)$. The endomorphism bundle $\operatorname{End}(E)$ has fiber $\operatorname{End}(E_p)$, and an endomorphism-valued form acts on an $E$-valued form by wedge in the form factors and evaluation in the fibers.

A @math:diffgeo:geometric-structures:df:bundle-connection $\nabla$ extends uniquely to the exterior covariant derivative $d_\nabla:\Omega^k(M;E)\to\Omega^{k+1}(M;E)$ by

$$
d_\nabla(\eta\otimes s)=d\eta\otimes s+(-1)^k\eta\w\nabla s
$$

for an ordinary $k$-form $\eta$ and a section $s$. Local decompositions into such terms determine the operator; the Leibniz rule for $\nabla$ makes it independent of moving a scalar factor between $\eta$ and $s$. In a local frame $d_\nabla\beta=d\beta+A\w\beta$. Its square on sections is curvature: $d_\nabla^2s=F_As$. Unlike the ordinary exterior derivative, its square need not vanish.

The induced connection on $\operatorname{End}(E)$ is the graded-commutator operator in @math:diffgeo:geometric-structures:th:bianchi. These constructions use the bundle transition rules of @math:diffgeo:bundles-flows:df:transition-functions.
