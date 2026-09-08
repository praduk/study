For an $n\times n$ matrix $A$ over a field, define

$$
\det A=\sum_{\sigma\in S_n}\operatorname{sgn}(\sigma)\prod_{i=1}^n A_{i,\sigma(i)},\qquad \operatorname{tr}A=\sum_{i=1}^n A_{ii}.
$$

Here $S_n$ is the permutation group and $\operatorname{sgn}(\sigma)=(-1)^{\#\{(i,j):i<j,\sigma(i)>\sigma(j)\}}$. For $n=0$ the determinant is $1$ and the trace is $0$.

For a finite-dimensional endomorphism, use a matrix in any basis. These scalars are independent of that choice: the permutation formula gives the alternating multilinear determinant and $\det(AB)=\det A\det B$ by expanding the columns, so $\det(P^{-1}AP)=\det A$; direct summation gives $\operatorname{tr}(BC)=\operatorname{tr}(CB)$ and hence trace invariance under conjugation.

The characteristic polynomial is $p_A(t)=\det(tI-A)$; the minimal polynomial is the monic polynomial of least degree with $m_A(A)=0$. Existence of a nonzero annihilating polynomial follows from linear dependence among the endomorphisms $I,A,A^2,\ldots$ in a finite-dimensional space. On the zero space the minimal polynomial is $1$. This entry concerns finite-dimensional algebraic traces and determinants; infinite-dimensional operator traces need additional hypotheses.
