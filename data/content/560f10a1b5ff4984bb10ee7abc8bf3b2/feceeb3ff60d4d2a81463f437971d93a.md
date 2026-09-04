Transfinite recursion defines ordinal arithmetic in the **right-hand argument**:

$$
\begin{aligned}
\alpha+0&=\alpha,&
\alpha+(\beta+1)&=(\alpha+\beta)+1,&
\alpha+\lambda&=\sup_{\beta<\lambda}(\alpha+\beta);\\
\alpha\cdot0&=0,&
\alpha\cdot(\beta+1)&=\alpha\cdot\beta+\alpha,&
\alpha\cdot\lambda&=\sup_{\beta<\lambda}(\alpha\cdot\beta);\\
\alpha^0&=1,&
\alpha^{\beta+1}&=\alpha^\beta\cdot\alpha,&
\alpha^\lambda&=\sup_{\beta<\lambda}\alpha^\beta
\quad(\alpha>0).
\end{aligned}
$$

Here $\lambda$ is a nonzero limit ordinal. For the zero base, the standard convention is

$$
0^0=1,
\qquad
0^\beta=0\quad(0<\beta).
$$

Thus the limit clause for exponentiation is deliberately restricted to positive bases: at a nonzero limit $\lambda$, the unqualified supremum of the earlier values would include $0^0=1$ and would not give the intended value $0^\lambda=0$. These operations describe order types of concatenated orders, lexicographically ordered products, and finite-support exponent constructions. They are ordinal operations, not cardinal operations.
