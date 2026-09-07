For a bounded $f:[a,b]\to\R$ with $a<b$ and a partition $P:a=x_0<\cdots<x_m=b$, put

$$
L(f,P)=\sum_{j=1}^m\inf_{[x_{j-1},x_j]}f\,(x_j-x_{j-1}),\quad
U(f,P)=\sum_{j=1}^m\sup_{[x_{j-1},x_j]}f\,(x_j-x_{j-1}).
$$

The lower integral is $\sup_P L(f,P)$ and the upper integral is $\inf_P U(f,P)$. The function is Riemann integrable exactly when they agree; their common value is $\int_a^b f$. We set $\int_a^a f=0$ and reverse the sign when reversing endpoints.
