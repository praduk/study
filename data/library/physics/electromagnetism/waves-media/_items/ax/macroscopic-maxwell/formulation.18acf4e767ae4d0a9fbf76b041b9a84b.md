A coarse-grained material model introduces polarization $\mathbf P$ and magnetization $\mathbf M$, with bound sources $\rho_b=-\nabla\cdot\mathbf P$ and $\mathbf j_b=\partial_t\mathbf P+\nabla\times\mathbf M$. Define $\mathbf D=\epsilon_0\mathbf E+\mathbf P$ and $\mathbf H=\mathbf B/\mu_0-\mathbf M$. Separating total sources into free and bound parts gives

$$
\nabla\cdot\mathbf D=\rho_f,\qquad \nabla\times\mathbf H=\mathbf j_f+\partial_t\mathbf D,
$$

with the homogeneous Maxwell equations unchanged. The coarse-graining and the physical assignment of bound versus free charge are modeling choices. These equations are not closed until the material response and free-current dynamics are specified.

On the material's spacetime split, set $\mathcal H=D_2+dt\w H_1$, where $D_2=\iota_{\mathbf D}\operatorname{vol}_3$ and $H_1=\mathbf H^\flat$. Then $d\mathcal H=\mathcal J_f$, while $dF=0$. This is the same exterior system as @physics:electromagnetism:spacetime-forms:th:maxwell-forms, but the constitutive relation between $F$ and $\mathcal H$ is supplied by the material. In a local linear model it is a linear map between two-form fibers; dispersive response is an operator on field histories. Neither is universally the vacuum Hodge star.
