Let a finite-dimensional Lie group $G$ act smoothly on $Q$. For $\xi$ in its @[Lie algebra]math:diffgeo:geometric-structures:df:lie-group, let $\xi_Q(q)=\left.\frac{d}{ds}\exp(s\xi)q\right|_{s=0}$. The cotangent lift sends $\alpha_q\in T_q^*Q$ to the covector at $gq$ given by

$$
g\cdot\alpha_q=(d(g^{-1})_{gq})^*\alpha_q.
$$

It preserves the tautological form $\theta$ and $\omega=-d\theta$ in @math:diffgeo:geometric-structures:th:cotangent-symplectic. A momentum map for this action is the map $J:T^*Q\to\mathfrak g^*$ defined by

$$
\langle J(\alpha_q),\xi\rangle=\alpha_q(\xi_Q(q))=:J_\xi(\alpha_q).
$$

More generally, for an action on a symplectic manifold, a momentum map satisfies $dJ_\xi=\iota_{\xi_P}\omega$ for every infinitesimal generator $\xi_P$, using our Hamiltonian sign convention. This condition does not assert existence for every symplectic action. The cotangent formula supplies one in the case above; @physics:classical:geometry:th:momentum-conservation proves the identity directly.
