The product rule for $\Delta_g=\operatorname{div}_g\operatorname{grad}_g$ gives the exact identity

$$
e^{-ik_0S/\varepsilon}(\varepsilon^2\Delta_g+k_0^2n^2)u_\varepsilon
=k_0^2(n^2-|dS|_g^2)a
+i\varepsilon k_0\bigl(2\langle da,dS\rangle_g+a\Delta_gS\bigr)
+\varepsilon^2\Delta_ga.
$$

Thus the two specified equations cancel the two leading coefficients. Multiply the transport equation by $\bar a$, take real parts, and use $2\operatorname{Re}(\bar a\,da)=d|a|^2$. The result is $\langle d|a|^2,dS\rangle_g+|a|^2\Delta_gS=\operatorname{div}_g j=0$.

By @math:diffgeo:forms:th:cartan, $d\iota_j\operatorname{vol}_g=\mathcal L_j\operatorname{vol}_g=(\operatorname{div}_g j)\operatorname{vol}_g$. Apply @math:diffgeo:stokes-cohomology:th:stokes to the compact tube. On its sides $j$ is tangent, so its flux form pulls back to zero; the two end integrals therefore cancel with their opposite boundary orientations.
