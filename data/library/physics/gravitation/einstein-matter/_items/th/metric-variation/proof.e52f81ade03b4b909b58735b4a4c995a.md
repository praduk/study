Write $q^{\mu\nu}=\delta g^{\mu\nu}$. Differentiate $g_{\mu\rho}g^{\rho\nu}=\delta_\mu^\nu$ to get $\delta g_{\mu\nu}=-g_{\mu\alpha}g_{\nu\beta}q^{\alpha\beta}$. The determinant derivative gives $\delta\sqrt{-g}=-\tfrac12\sqrt{-g}g_{\mu\nu}q^{\mu\nu}$, where $\sqrt{-g}=\sqrt{-\det g}$.

Let $C^\rho_{\mu\nu}=\delta\Gamma^\rho_{\mu\nu}$. It is a tensor, as a variation of a connection. Differentiation of the curvature formula gives

$$
\delta R_{\mu\nu}=\nabla_\rho C^\rho_{\nu\mu}-\nabla_\nu C^\rho_{\rho\mu}.
$$

Indeed the partial-derivative terms are $\partial_\rho C^\rho_{\nu\mu}-\partial_\nu C^\rho_{\rho\mu}$; the four product-rule terms from the two connection products are exactly the connection corrections to these two covariant derivatives, using symmetry of their lower indices. Metric compatibility then makes $g^{\mu\nu}\delta R_{\mu\nu}=\nabla_\rho V^\rho$ for $V^\rho=g^{\mu\nu}C^\rho_{\mu\nu}-g^{\mu\rho}C^\lambda_{\lambda\mu}$. Its integral vanishes because $\sqrt{-g}\nabla_\rho V^\rho=\partial_\rho(\sqrt{-g}V^\rho)$ and $V$ has compact support.

Vary $R=g^{\mu\nu}R_{\mu\nu}$ and the volume element. The surviving terms give

$$
\delta(S_g+S_m)=\int\sqrt{-g}\left[\frac{c^3}{16\pi G}(G_{\mu\nu}+\Lambda g_{\mu\nu})-\frac1{2c}T_{\mu\nu}\right]q^{\mu\nu}\,d^4x.
$$

The coefficient is symmetric. Arbitrary compactly supported symmetric $q$ and the fundamental lemma of variations force it to vanish pointwise. Multiplying by $16\pi G/c^3$ yields Einstein's equation. Conversely that equation makes every such first variation vanish.
