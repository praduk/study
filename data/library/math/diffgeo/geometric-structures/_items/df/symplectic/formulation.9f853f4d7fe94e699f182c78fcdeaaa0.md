A symplectic manifold is a @[smooth manifold]math:diffgeo:manifolds:df:smooth-manifold $P$ equipped with a closed nondegenerate two-form $\omega$. Nondegenerate means $X\mapsto\iota_X\omega$ is an isomorphism $T_pP\to T_p^*P$ at every point. In positive dimension this forces $\dim P=2n$. The convention in this library is

$$
\iota_{X_H}\omega=dH,\qquad \{f,g\}=df(X_g)=\omega(X_f,X_g).
$$

Here $H,f,g$ are smooth real functions, $X_H$ is the Hamiltonian vector field, and $\{f,g\}$ is the Poisson bracket. These definitions use @math:diffgeo:forms:df:interior-lie and @math:diffgeo:forms:df:exterior-derivative. They do not require a metric. In canonical coordinates $\omega=\sum_i dq^i\w dp_i$, one gets $X_H=\sum_i(H_{p_i}\partial_{q^i}-H_{q^i}\partial_{p_i})$.

A submanifold is isotropic when its pulled-back two-form vanishes, and Lagrangian when it is isotropic of dimension $n$. A @[diffeomorphism]math:diffgeo:manifolds:df:smooth-map $\Phi$ is symplectic when $\Phi^*\omega=\omega$. With the displayed convention $[X_f,X_g]=-X_{\{f,g\}}$; some texts use the opposite Hamiltonian-vector-field convention.
