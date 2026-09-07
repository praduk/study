Fix $0<\rho<r<R$. For $|z-a|\le\rho$ and $|\zeta-a|=r$, expand

$$
\frac1{\zeta-z}=\sum_{n=0}^{\infty}\frac{(z-a)^n}{(\zeta-a)^{n+1}}.
$$

The ratio is bounded by $\rho/r<1$, so the series is uniformly convergent on the circle uniformly in $z$. Insert it into Cauchy's formula and integrate termwise, obtaining a power series with the displayed integral coefficients. Power series can be differentiated termwise inside their convergence disk, so $f$ has derivatives of every order and the $n$th coefficient equals $f^{(n)}(a)/n!$. Every point inside $D(a,R)$ lies in such a smaller disk.
