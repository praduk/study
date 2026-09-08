Write $d=d_3+dt\w\partial_t$ on time-dependent spatial forms. The graded product rule gives

$$
dF=d_3B_2+dt\w(\partial_tB_2+d_3e).
$$

Here $d_3B_2=(\nabla\cdot\mathbf B)\operatorname{vol}_3$ and $d_3e=\iota_{\nabla\times\mathbf E}\operatorname{vol}_3$. Its two independent spatial/time components are exactly the magnetic Gauss and Faraday equations.

Similarly,

$$
d\mathcal H=\epsilon_0(\nabla\cdot\mathbf E)\operatorname{vol}_3
+dt\w\bigl(\epsilon_0\partial_t\star_3e-\mu_0^{-1}d_3b\bigr).
$$

Equating its components with $\mathcal J$ gives $\nabla\cdot\mathbf E=\rho/\epsilon_0$ and $\nabla\times\mathbf B=\mu_0\mathbf j+\mu_0\epsilon_0\partial_t\mathbf E$. Each decomposition is unique, proving both directions. The vector identities used here follow by expanding the @math:diffgeo:forms:df:exterior-derivative in an oriented Cartesian coframe.

For the stated curved model, at any point choose oriented normal coordinates. First derivatives of $g$ vanish there, so the same pointwise calculation gives the component equations with covariant derivatives. Both sides are tensors, so equality in that chart at each point proves their coordinate-independent equivalence. This does not derive the curved physical model from the flat one.
