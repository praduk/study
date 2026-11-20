Use the @[subring test]mt4-subring with the @[pointwise operations]mt4-function-ring.

**(a) Yes.** Zero belongs. At each rational point, the difference and product of two functions that vanish there also vanish.

**(b) Yes.** If $f,g$ are restrictions of $p,q\in\R[x]$, then $f-g$ and $fg$ are the restrictions of $p-q$ and $pq$ in the @[polynomial ring]mt4-polynomial-ring. The zero polynomial supplies zero.

**(c) No.** Let $h$ be zero on $[0,1/2]$ and one on $(1/2,1]$. Both $1+h$ and $1$ are nowhere zero. Their difference $h$ has infinitely many zeros and satisfies $h(1)=1$.

**(d) No.** The same $h$ vanishes on $[0,1/2]$, while $1-h$ vanishes on $(1/2,1]$. Both zero sets are infinite, but their sum is the constant function $1$.

**(e) Yes.** The zero function qualifies. The @[arithmetic laws for finite limits]gre:mathematics-subject-test:single-variable-calculus:th:limit-arithmetic give left limits $0-0$ and $0\cdot0$. The functions' values at $1$ do not affect this test.

**(f) Yes.** The @[rational span]math:algebra:linear-foundations:df:basis-dimension contains zero and is closed under subtraction. For $u=nx$ and $v=mx$, apply the product formulas for @[two sines]gre:mathematics-subject-test:trigonometry:th:sine-sine-product, @[two cosines]gre:mathematics-subject-test:trigonometry:th:cosine-cosine-product, and @[a sine and a cosine]gre:mathematics-subject-test:trigonometry:th:sine-cosine-product.

$$
\begin{aligned}
2\sin u\sin v&=\cos(u-v)-\cos(u+v),\\
2\cos u\cos v&=\cos(u-v)+\cos(u+v),\\
2\sin u\cos v&=\sin(u+v)+\sin(u-v).
\end{aligned}
$$

All coefficients are rational. @[The parity identities]gre:mathematics-subject-test:trigonometry:th:trig-parity turn any negative frequency into a nonnegative one. Distributing proves product closure for the entire span.
