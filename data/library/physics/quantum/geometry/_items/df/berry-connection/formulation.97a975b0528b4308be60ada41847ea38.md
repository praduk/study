Let $P(\lambda)$ be a smooth rank-one orthogonal projector in $\C^n$ over a parameter manifold. Its images form a complex line bundle. On a chart choose a smooth unit vector $\psi(\lambda)$ spanning the line. The Berry connection one-form in this choice is

$$
\mathcal A=i\langle\psi,d\psi\rangle,
\qquad \mathcal B=d\mathcal A.
$$

Normalization makes $\langle\psi,d\psi\rangle$ purely imaginary, hence $\mathcal A$ is real. A horizontal lift along a path is a unit section $\widetilde\psi=e^{i\gamma}\psi$ satisfying $\langle\widetilde\psi,\dot{\widetilde\psi}\rangle=0$; thus $\dot\gamma=\mathcal A(\dot\lambda)$. The resulting phase around a closed path is the holonomy $e^{i\gamma}$. If a single-valued unit frame covers the loop, it is $\exp(i\oint\mathcal A)$; otherwise local frames must be patched with their transition phases.

For a smooth family of Hamiltonians with an isolated simple eigenvalue, its eigenspace supplies such a projector. This holonomy is the geometric part of the phase in a valid isolated-eigenstate adiabatic approximation. The definition alone gives no adiabatic error bound and does not cover degeneracies by a scalar phase. The physical connection was established in Berry's original [Quantal phase factors accompanying adiabatic changes](https://michaelberryphysics.wordpress.com/wp-content/uploads/2013/07/berry120.pdf), §2, whose phase convention is used here. General bundle language is in @math:diffgeo:geometric-structures:df:bundle-connection.
