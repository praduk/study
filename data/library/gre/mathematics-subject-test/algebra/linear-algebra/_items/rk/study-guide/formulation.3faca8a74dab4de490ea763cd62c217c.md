## Matrix algebra and linear systems

- Matrix multiplication is composition and is generally not commutative. Useful identities include $(AB)^{-1}=B^{-1}A^{-1}$ and $(AB)^T=B^TA^T$.
- A square matrix is invertible exactly when its determinant is nonzero, its rank is full, its nullspace is zero, and $Ax=b$ has a unique solution for every $b$.
- For a system, compare the coefficient and augmented ranks: unequal ranks mean no solution; equal rank below the number of variables means infinitely many; full column rank gives uniqueness when consistent.
- Row replacement preserves determinant, a row swap changes its sign, and scaling a row scales the determinant. Triangular determinants are products of diagonal entries.

## Vector spaces and linear transformations

- To test a proposed subspace, check zero, addition, and scalar multiplication. A basis is both independent and spanning, and all bases of a finite-dimensional space have the same size.
- Rank-nullity is $\dim V=\dim\ker T+\dim\operatorname{im}T$. Injective means zero kernel; surjective means image equal to the codomain.
- The columns of a transformation matrix are the coordinates of the images of the ordered domain-basis vectors. Basis order matters.

## Characteristic polynomials and eigenstructure

- With $\chi_A(\lambda)=\det(\lambda I-A)$, its roots are the eigenvalues. Triangular matrices reveal eigenvalues on the diagonal; trace and determinant give their sum and product with algebraic multiplicity.
- Geometric multiplicity is $\dim\ker(A-\lambda I)$ and never exceeds algebraic multiplicity. An $n\times n$ matrix is diagonalizable exactly when it has $n$ independent eigenvectors.

## Recognition cues and traps

Look first for triangular or block-triangular form, repeated rows, an identity such as $A^2=cI$, and a rank-nullity shortcut. Do not confuse row-equivalent matrices with similar matrices, algebraic with geometric multiplicity, or coordinate columns with rows.
