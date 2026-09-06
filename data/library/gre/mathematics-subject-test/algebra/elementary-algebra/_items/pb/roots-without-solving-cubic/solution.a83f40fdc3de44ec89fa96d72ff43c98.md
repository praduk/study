**Fastest valid route.** Use Vieta rather than solving the cubic. For a monic cubic

$$x^3-a x^2+b x-c,$$

we have $rs+rt+st=b$ and $rst=c$. Here $b=-1$ and $c=-4$, so

$$\frac1r+\frac1s+\frac1t=\frac{rs+rt+st}{rst}=\frac{-1}{-4}=\frac14.$$

Thus the answer is **(D)**.

As a check, the polynomial factors as $(x-4)(x-1)(x+1)$, whose reciprocal roots sum to $1/4+1-1=1/4$.
