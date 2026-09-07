Place an auxiliary charge $-q$ at $(0,0,-a)$ outside the physical domain. With $R_\pm=\sqrt{x^2+y^2+(z\mp a)^2}$, take $\phi=q(R_+^{-1}-R_-^{-1})/(4\pi\epsilon_0)$. It has the correct singularity, is harmonic elsewhere in $z>0$, and is zero when $z=0$.

Using the outward normal from the conductor, $\sigma=\epsilon_0E_z(0^+)=-qa/[2\pi(s^2+a^2)^{3/2}]$, where $s=\sqrt{x^2+y^2}$. Thus

$$
Q_{\rm induced}=2\pi\int_0^\infty\sigma(s)s\,ds=-qa\int_0^\infty\frac{s\,ds}{(s^2+a^2)^{3/2}}=-q.
$$

For uniqueness, the difference of two candidates extends harmonically across the charge since their singular parts cancel. On a large half-ball it is zero on the flat boundary and bounded in absolute value on the hemisphere by a number tending to zero. The maximum principle applied to the difference and its negative gives zero at every fixed interior point. The auxiliary charge represents boundary data; it is not a second physical charge above the conductor.
