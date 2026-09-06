**Correct choice: (C).**

**Fastest valid route.** Apply Cauchy's derivative formula with $f(z)=z^2+1$, $a=1$, and $n=2$:

$$
\oint_C\frac{f(z)}{(z-1)^3}\,dz
=\frac{2\pi i}{2!}f''(1).
$$

Since $f''(z)=2$, the integral is $2\pi i$.

**Verification.** The Taylor expansion about $z=1$ is

$$
z^2+1=2+2(z-1)+(z-1)^2.
$$

Dividing by $(z-1)^3$ makes the coefficient of $(z-1)^{-1}$ equal to $1$. Thus the residue is $1$, and positive orientation gives $2\pi i$.
