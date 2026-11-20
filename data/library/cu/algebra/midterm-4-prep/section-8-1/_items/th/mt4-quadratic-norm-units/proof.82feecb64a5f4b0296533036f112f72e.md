Write $z=a+b\sqrt D$ and $w=c+d\sqrt D$ with rational coefficients. In the @[quadratic norm formula]mt4-quadratic-integers-norm, conjugation replaces $\sqrt D$ by $-\sqrt D$. Expanding $zw$ shows $\overline{zw}=\bar z\bar w$, since $(-\sqrt D)^2=D$. Therefore $N(zw)=(z\bar z)(w\bar w)=N(z)N(w)$.

For $z=m+n\omega$ in the quadratic integer ring, take $m,n\in\Z$. Then

$$
N(z)=m^2+mn(\omega+\bar\omega)+n^2\omega\bar\omega.
$$

If $\omega=(1+\sqrt D)/2$, the last two coefficients are $1$ and $(1-D)/4\in\Z$. If $\omega=\sqrt D$, they are $0$ and $-D$. In either case $N(z)\in\Z$. Also $\bar\omega=1-\omega$ or $-\omega$, respectively, so $\bar z\in\mathcal O$.

If $z$ is a @[unit]mt4-unit with inverse $w\in\mathcal O$, the integers $N(z),N(w)$ multiply to $N(1)=1$. Thus $N(z)=\pm1$. Conversely, when $N(z)=\pm1$ the element $\bar z/N(z)$ lies in $\mathcal O$ and its product with $z$ is $1$.
