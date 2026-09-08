Additivity and order bounds for the integral give

$$
\left|\frac{F(x+h)-F(x)}h-f(x)\right|
\le\sup_{t\text{ between }x\text{ and }x+h}|f(t)-f(x)|.
$$

Continuity makes the right side tend to zero. The same bound with bounded $f$ shows that $F$ is continuous on $[a,b]$. Since $(G-F)'=0$ on $(a,b)$, the @[mean value theorem]math:uganalysis:differentiation:th:mean-value makes $G-F$ constant, including at endpoints by continuity. Therefore $G(b)-G(a)=F(b)-F(a)=\int_a^b f$.
