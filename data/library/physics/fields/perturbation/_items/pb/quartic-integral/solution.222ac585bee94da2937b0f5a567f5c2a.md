Gaussian integration by parts gives $\mathbb E[X^{2n}]=(2n-1)\mathbb E[X^{2n-2}]$, starting with one. Hence $\mathbb E[X^4]=3$, $\mathbb E[X^8]=105$, and $\mathbb E[X^{12}]<\infty$. Taylor's theorem for $e^{-u}$ on $u\ge0$ bounds the absolute remainder after the quadratic term by $u^3/6$. Taking expectations yields

$$
Z(\lambda)=1-\frac{\lambda}{8}+\frac{35\lambda^2}{384}+O(\lambda^3).
$$

The remainder is bounded by $\lambda^3\mathbb E[X^{12}]/(6\cdot24^3)$. This is a controlled one-sided finite-dimensional expansion, not a proof of convergence of the full perturbation series.
