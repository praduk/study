**Fastest valid route.** The matrix is block triangular, so

$$\chi_A(\lambda)=(\lambda-2)^2(\lambda+1).$$

Thus $2$ has algebraic multiplicity $2$. For its eigenspace,

$$A-2I=\begin{pmatrix}0&1&0\\0&0&0\\1&0&-3\end{pmatrix}.$$

The equations are $y=0$ and $x=3z$, leaving one free parameter. Therefore

$$\dim\ker(A-2I)=1.$$

The answer is **(D)**. In particular, the deficient eigenspace also shows that $A$ is not diagonalizable.
