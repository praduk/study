## Systems, matrices, and determinants

Row reduction preserves the solution set. Pivot columns in the original matrix form a basis for the column space; nonzero rows of row-echelon form give a basis for the row space.

$$
(AB)^T=B^TA^T,\qquad (AB)^{-1}=B^{-1}A^{-1},\qquad
\det(AB)=\det A\det B.
$$

For $A\in M_n$, $\det(cA)=c^n\det A$. A row swap changes determinant sign, row scaling scales it, and row replacement leaves it unchanged.

For $A=\begin{pmatrix}a&b\\c&d\end{pmatrix}$,

$$
\det A=ad-bc,\qquad
A^{-1}=\frac1{ad-bc}\begin{pmatrix}d&-b\\-c&a\end{pmatrix}.
$$

## Vector spaces and dimension

A basis is linearly independent and spanning. Every basis of a finite-dimensional space has the same size. For $T:V\to W$,

$$
\dim V=\dim\ker T+\dim\operatorname{im}T.
$$

For finite-dimensional subspaces,

$$
\dim(U+W)=\dim U+\dim W-\dim(U\cap W).
$$

For an $m\times n$ matrix, rank plus nullity equals $n$. The invertible-matrix theorem ties together nonzero determinant, full rank, independent columns, spanning columns, unique solutions, and $0$ not being an eigenvalue.

## Eigenvalues and diagonalization

$$
Av=\lambda v,\qquad \chi_A(\lambda)=\det(\lambda I-A).
$$

Counting algebraic multiplicity,

$$
\operatorname{tr}A=\sum\lambda_i,\qquad \det A=\prod\lambda_i.
$$

Triangular matrices reveal eigenvalues on the diagonal. Similar matrices have the same characteristic polynomial, determinant, trace, and eigenvalues.

$A$ is diagonalizable iff it has a basis of eigenvectors. Distinct eigenvalues guarantee diagonalizability. For each eigenvalue, geometric multiplicity is at most algebraic multiplicity; equality for every eigenvalue is equivalent to diagonalizability.

## Inner products and orthogonality

$$
\operatorname{proj}_{\mathbf u}\mathbf v=
\frac{\mathbf v\cdot\mathbf u}{\mathbf u\cdot\mathbf u}\mathbf u.
$$

For an orthonormal basis $u_1,\dots,u_k$ of $W$,

$$
\operatorname{proj}_Wv=\sum_{j=1}^k\langle v,u_j\rangle u_j.
$$

Real symmetric matrices have real eigenvalues and an orthonormal eigenbasis. Orthogonal matrices satisfy $Q^{-1}=Q^T$, preserve norms and angles, and have complex eigenvalues of modulus $1$.

## Fast recognition

Use trace and determinant before expanding a characteristic polynomial, rank-nullity before solving a full kernel, and columns of the images of basis vectors to build a transformation matrix. Watch whether a change-of-basis matrix maps old coordinates to new or the reverse.
