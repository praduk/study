For smooth fields satisfying Maxwell's equations, a fixed oriented smooth surface $S$ with consistently oriented boundary $C$ satisfies

$$
\oint_C\mathbf E\cdot d\boldsymbol\ell=-\frac{d}{dt}\int_S\mathbf B\cdot\mathbf n\,dS,
$$

$$
\oint_C\mathbf B\cdot d\boldsymbol\ell=\mu_0\int_S\mathbf j\cdot\mathbf n\,dS+c^{-2}\frac{d}{dt}\int_S\mathbf E\cdot\mathbf n\,dS.
$$

For a bounded smooth volume $V$, the fluxes of $\mathbf E$ and $\mathbf B$ through $\partial V$ are respectively $\epsilon_0^{-1}\int_V\rho\,dV$ and zero.

All four integral statements are applications of @math:diffgeo:stokes-cohomology:th:stokes to the field and excitation forms in @physics:electromagnetism:spacetime-forms:th:maxwell-forms. For moving surfaces, use @math:diffgeo:geometric-structures:th:transport-form; its Lie derivative supplies the extra transport term.
