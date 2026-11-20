**Strategy.** Apply the @[subring test]mt4-subring to each set. For a positive answer, exhibit zero and check closure under subtraction and multiplication using the @[pointwise operations]mt4-function-ring. For a negative answer, one failed closure property suffices.

**(a) Yes. Vanishing at rational points survives both operations.** The zero function qualifies. If $f$ and $g$ vanish at every rational $q\in[0,1]$, then $(f-g)(q)=0-0=0$ and $(fg)(q)=0\cdot0=0$ for every such $q$.

**(b) Yes. Differences and products are still polynomial functions.** The zero polynomial supplies the zero function. If $f$ and $g$ are restrictions of polynomials $p$ and $q$, then $f-g$ and $fg$ are the restrictions of $p-q$ and $pq$. Both belong to the @[polynomial ring]mt4-polynomial-ring $\R[x]$.

**(c) No. Subtraction can introduce infinitely many zeros.** Let $h$ equal $0$ on $[0,1/2]$ and $1$ on $(1/2,1]$. The functions $1+h$ and $1$ are both nowhere zero. Their difference is $h$, which has infinitely many zeros and takes the value $1$ at $1$. It lies outside the set.

**(d) No. Addition can remove all zeros.** With $h$ as in (c), both $h$ and $1-h$ have infinitely many zeros, on the left and right halves respectively. Their sum is the constant function $1$, which has no zeros. A subring must be closed under addition.

**(e) Yes. A zero left limit survives both operations.** The zero function qualifies. If $f,g\to0$ as $x\to1^-$, the @[laws for finite limits]gre:mathematics-subject-test:single-variable-calculus:th:limit-arithmetic give $f-g\to0-0=0$ and $fg\to0\cdot0=0$.

**(f) Yes. Products of generators are still trigonometric sums.** The @[rational span]math:algebra:linear-foundations:df:basis-dimension contains zero and is closed under subtraction. By distributivity it suffices to check products of two generators. For $u=nx$ and $v=mx$, use the identities for @[two sines]gre:mathematics-subject-test:trigonometry:th:sine-sine-product, @[two cosines]gre:mathematics-subject-test:trigonometry:th:cosine-cosine-product, and @[a sine and a cosine]gre:mathematics-subject-test:trigonometry:th:sine-cosine-product.

$$
\begin{aligned}
2\sin u\sin v &= \cos(u-v)-\cos(u+v),\\
2\cos u\cos v &= \cos(u-v)+\cos(u+v),\\
2\sin u\cos v &= \sin(u+v)+\sin(u-v).
\end{aligned}
$$

Dividing by $2$ gives rational coefficients. If $n-m<0$, the @[parity identities]gre:mathematics-subject-test:trigonometry:th:trig-parity replace the negative frequency by a nonnegative one. Every generator product therefore belongs to the span.
