Let $\Omega\subset\mathbb R^n$ be open. A test function is an element of $C_c^\infty(\Omega)$, the smooth functions with @[compact support]math:diffgeo:manifolds:df:partition-unity in $\Omega$. A distribution $T$ is a linear functional on these test functions such that for every compact $K\subset\Omega$ there are $C\ge0$ and an integer $m\ge0$ with

$$
|T(\phi)|\le C\max_{|\alpha|\le m}\sup_K|\partial^\alpha\phi|
\quad\text{whenever }\operatorname{supp}\phi\subset K.
$$

Here a multi-index $\alpha=(\alpha_1,\ldots,\alpha_n)$ has nonnegative integer entries, $|\alpha|=\sum_i\alpha_i$, and $\partial^\alpha=\partial_1^{\alpha_1}\cdots\partial_n^{\alpha_n}$. This bound is the continuity condition in the usual test-function topology. We use a bilinear distribution-test-function pairing, without complex conjugation.

A locally integrable function $f$ defines $T_f(\phi)=\int f\phi$. The point distribution $\delta_a(\phi)=\phi(a)$ is continuous by the bound with $m=0$. Distributional differentiation is $(\partial^\alpha T)(\phi)=(-1)^{|\alpha|}T(\partial^\alpha\phi)$. This extends classical differentiation by integration by parts. It is unrelated to a tangent-plane @math:diffgeo:bundles-flows:df:distribution despite the shared word.
