On a pseudo-Riemannian manifold, a Killing field is a vector field $K$ with $\mathcal L_Kg=0$. Equivalently, its local flow preserves $g$. For the Levi-Civita connection this is

$$
g(\nabla_XK,Y)+g(X,\nabla_YK)=0
$$

for all vector fields $X,Y$, or $\nabla_iK_j+\nabla_jK_i=0$ in coordinates. To check the equivalence, expand $(\mathcal L_Kg)(X,Y)=K g(X,Y)-g([K,X],Y)-g(X,[K,Y])$ and use @math:diffgeo:connections:df:torsion-compatibility. The equivalence with flow invariance follows by differentiating $\Phi_t^*g$.

In a chart, $\partial_i$ is Killing exactly when the metric components are independent of $x^i$. This criterion refers to the entire tensor in that chart. A general spacetime need not have any nonzero Killing field; conserved quantities associated with spacetime symmetry therefore require that symmetry as a hypothesis.
