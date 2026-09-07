If $f$ is holomorphic on $r<|z-a|<R$, where $0\le r<R\le\infty$, then it has a unique Laurent expansion

$$
f(z)=\sum_{n=-\infty}^{\infty}c_n(z-a)^n.
$$

Both its nonnegative-power and negative-power series converge absolutely and uniformly on compact subannuli. For any $r<\rho<R$,

$$
c_n=\frac1{2\pi i}\int_{|\zeta-a|=\rho}\frac{f(\zeta)}{(\zeta-a)^{n+1}}\,d\zeta.
$$

The existence proof by applying Cauchy theory between two concentric circles is not included; see Lebl, [Guide to Cultivating Complex Analysis, Section 4.4](https://www.jirka.org/ca/ca.pdf). The inner and outer radii matter: the same rational function may have different Laurent expansions on different annuli.
