The permutation $\pi(x)$ sends $g$ to $xg$. Starting at a point $g$, its successive images are

$$
g,xg,x^2g,\ldots,x^{n-1}g,
$$

and its next image is $x^ng=g$. If $x^ig=x^jg$, right cancellation gives $x^{i-j}=1$, so $i\equiv j\pmod n$. Thus these $n$ points are distinct and form one cycle of length exactly $n$. This argument applies to every $g$, so every cycle has length $n$.

The cycles partition the $mn$ elements of $G$, giving exactly $m$ disjoint $n$-cycles. A cycle of length $n$ is a product of $n-1$ transpositions, hence has sign $(-1)^{n-1}$. Multiplicativity of sign gives

$$
\sgn(\pi(x))=(-1)^{m(n-1)}.
$$

This equals $-1$ precisely when $m(n-1)$ is odd, which happens exactly when $m$ is odd and $n-1$ is odd, or equivalently when $m$ is odd and $n$ is even. For $x=1$, $n=1$ and the result says the identity is a product of $|G|$ fixed-point cycles and is even, as expected.

**Technique:** compute the period of one arbitrary point by cancellation; uniform cycle lengths follow without writing the whole permutation.

**Foundations:** @cu:algebra:midterm-2:theorems:th:coset-action, @cu:algebra:midterm-2:theorems:th:first-isomorphism.
