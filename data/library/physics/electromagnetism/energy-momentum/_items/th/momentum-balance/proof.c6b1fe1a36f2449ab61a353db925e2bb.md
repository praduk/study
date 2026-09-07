For any smooth vector field $\mathbf a$, differentiation gives

$$
\nabla\cdot(\mathbf a\mathbf a^T-\tfrac12|\mathbf a|^2I)=(\nabla\cdot\mathbf a)\mathbf a-\mathbf a\times(\nabla\times\mathbf a).
$$

Apply this to $\mathbf E$ and $\mathbf B$. Maxwell's equations yield

$$
\nabla\cdot\sigma=\rho\mathbf E+\epsilon_0\mathbf E\times\partial_t\mathbf B+\mathbf j\times\mathbf B+\epsilon_0(\partial_t\mathbf E)\times\mathbf B.
$$

The last two time-dependent terms together are $\partial_t\mathbf g$. Rearrangement proves the local identity, and the divergence theorem proves the integral statement.
