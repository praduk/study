Let $Q$ be a smooth configuration manifold with a @[positive definite]math:algebra:linear-foundations:df:bilinear-forms @math:diffgeo:connections:df:riemannian-metric $g$ and smooth potential $V:Q\to\R$. The natural mechanical Lagrangian is the function on its tangent bundle

$$
L(q,v)=\tfrac12g_q(v,v)-V(q).
$$

Here $g$ includes the masses: for Cartesian particles, $g=\sum_a m_a\,dx_a\cdot dx_a$. Its evaluation on a physical velocity has energy units. In arbitrary generalized coordinates the units of $g_{ij}$ compensate those of $\dot q^i\dot q^j$.

The fiber derivative $\mathbb FL:TQ\to T^*Q$, defined by $(\mathbb FL(q,v))(w)=\left.\frac{d}{ds}L(q,v+sw)\right|_{s=0}$, is $v\mapsto g_q(v,\cdot)$. It is an isomorphism on every fiber. Consequently

$$
H(q,p)=\tfrac12g_q^{-1}(p,p)+V(q).
$$

This is the global version of @physics:classical:hamilton:df:legendre. The metric belongs to configuration space; the @math:diffgeo:geometric-structures:th:cotangent-symplectic form on phase space is supplied by the cotangent bundle and does not require this metric. General regular Lagrangians need not have this quadratic form.
