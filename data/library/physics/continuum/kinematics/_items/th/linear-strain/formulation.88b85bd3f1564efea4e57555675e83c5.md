If $\chi(X)=X+u(X)$, then

$$
E=\varepsilon+\tfrac12(\nabla u)^T\nabla u,\qquad
\varepsilon=\tfrac12(\nabla u+(\nabla u)^T).
$$

For a unit material direction $n$, its fractional length change is $n^T\varepsilon n+O(|\nabla u|^2)$ as $\nabla u\to0$. The volume ratio is $J=1+\operatorname{div}u+O(|\nabla u|^2)$.

The intrinsic infinitesimal change of a fixed @[Riemannian metric]math:diffgeo:connections:df:riemannian-metric along a displacement field $u$ is $\tfrac12\mathcal L_ug$. For the Levi-Civita connection, its value on vectors $X,Y$ is $\tfrac12[g(\nabla_Xu,Y)+g(X,\nabla_Yu)]$: expand the Lie derivative of a covariant tensor and use metric compatibility and zero torsion. In Euclidean Cartesian coordinates this is precisely the matrix $\varepsilon$ above, and links finite strain to the metric pullback in @physics:continuum:kinematics:df:finite-strain.
