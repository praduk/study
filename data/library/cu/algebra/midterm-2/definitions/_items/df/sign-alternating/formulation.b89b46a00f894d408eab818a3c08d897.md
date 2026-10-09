Every permutation in $S_n$ can be written as a product of transpositions. Its sign is $+1$ when the number of transpositions is even and $-1$ when odd; the parity is independent of the expression. The sign map is a homomorphism $\sgn:S_n\to\{1,-1\}$. For $n\ge2$ it is surjective, and

$$
A_n=\ker(\sgn),\qquad |A_n|=n!/2.
$$

A $k$-cycle has sign $(-1)^{k-1}$; signs multiply over disjoint cycles. Thus a permutation is odd exactly when its disjoint-cycle decomposition has an odd number of even-length cycles.

The lecture justifies well-definedness using $D=\prod_{i<j}(x_i-x_j)$ over a field of characteristic not $2$: permuting variables takes $D$ to $D$ or $-D$, and transpositions take it to $-D$. Applying two permutations gives multiplicativity. This polynomial argument is an explanation of sign, not an extra hypothesis on the abstract group $S_n$.

Example: $(1\ 2)(3\ 4)$ is even although it has order $2$. For $n=1$, $A_1=S_1=1$, so the formula $n!/2$ is not applicable.
