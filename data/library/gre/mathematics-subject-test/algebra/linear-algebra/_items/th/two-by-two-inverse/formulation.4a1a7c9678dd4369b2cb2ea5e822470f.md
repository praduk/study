If $A=\begin{pmatrix}a&b\\c&d\end{pmatrix}$, then $\det A=ad-bc$. When $ad-bc\ne0$,

$$
A^{-1}=\frac1{ad-bc}\begin{pmatrix}d&-b\\-c&a\end{pmatrix}.
$$

For $ad-bc=0$, no inverse exists.

**Recognition cue.** A tiny inverse can be faster than row reduction; sometimes only one entry is needed.

**Boundary check.** Swap diagonal entries and negate off-diagonal entries, then divide every entry by the determinant.

**Practice different uses:**

- @gre:mathematics-subject-test:algebra:linear-algebra:pb:inverse-entry
- @gre:mathematics-subject-test:algebra:linear-algebra:pb:two-sided-matrix-equation
- @gre:mathematics-subject-test:algebra:linear-algebra:pb:two-variable-system-inverse
