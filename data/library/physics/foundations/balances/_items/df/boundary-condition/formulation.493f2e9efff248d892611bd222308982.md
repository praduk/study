Initial data describe preparation on a time slice. A boundary condition describes coupling to the exterior or an idealized wall. For a scalar field $u$, Dirichlet data prescribe $u$, Neumann data its normal derivative (or a specified physical flux), and Robin data a stated linear combination.

A boundary condition must match the equation and material law. For heat conduction $j_Q=-\kappa\nabla T$ with conductivity $\kappa>0$, insulation means $j_Q\cdot n=0$; it does not mean $T=0$. Fixing a temperature models a reservoir, which can exchange energy.
