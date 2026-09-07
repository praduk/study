Let $A$ be a real matrix with all eigenvalues of negative real part and let $b$ be a fixed vector. For $\dot x=Ax+b u(t)$ with scalar continuous input, the solution is

$$
x(t)=e^{A(t-t_0)}x(t_0)+\int_{t_0}^te^{A(t-s)}b u(s)\,ds.
$$

For bounded continuous input on the whole real line, the unique solution bounded for all time is $x(t)=\int_{-\infty}^t e^{A(t-s)}b u(s)\,ds$.
