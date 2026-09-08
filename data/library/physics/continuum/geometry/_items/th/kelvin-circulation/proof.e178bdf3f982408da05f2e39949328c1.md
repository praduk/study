Metric compatibility and zero torsion imply, for any vector field $w$,

$$
du(v,w)=g(\nabla_vv,w)-g(\nabla_wv,v)
=g(\nabla_vv,w)-d(\tfrac12|v|_g^2)(w).
$$

Consequently $(\nabla_vv)^\flat=\iota_vdu+d(|v|_g^2/2)$. Lower the index in the assumed Euler equation and use $\mathcal L_vu=\iota_vdu+d(u(v))$ from @math:diffgeo:forms:th:cartan, with $u(v)=|v|_g^2$. This gives the displayed one-form equation, including its minus sign before kinetic energy on the right.

The exterior derivative commutes with $\partial_t$ and with $\mathcal L_v$; the latter follows immediately from Cartan's formula and $d^2=0$. Applying $d$ therefore gives advection of $\Omega$. Finally @math:diffgeo:geometric-structures:th:transport-form differentiates circulation along a material curve. Its derivative is the integral of the exact one-form on the right, which vanishes on a closed curve by the fundamental theorem of calculus, or by @math:diffgeo:stokes-cohomology:th:stokes on a one-dimensional domain with empty boundary. The curve need not bound a surface.
