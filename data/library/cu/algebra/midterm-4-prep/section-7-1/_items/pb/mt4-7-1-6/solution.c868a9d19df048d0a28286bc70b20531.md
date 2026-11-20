Use the @[subring test]mt4-subring with the @[pointwise operations]mt4-function-ring.

**(a) Yes.** Zero belongs. At each rational point, the difference and product of two functions that vanish there also vanish.

**(b) Yes.** The zero polynomial, differences of polynomials, and products of polynomials all restrict to functions of the required kind.

**(c) No.** Let $h$ equal $1$ at irrational points and $0$ at rational points. Both $1+h$ and $1$ are nowhere zero. Their difference $h$ has infinitely many zeros and takes the value $1$ somewhere.

**(d) No.** With the same $h$, both $h$ and $1-h$ have infinitely many zeros. Their sum is the constant function $1$.

**(e) Yes.** The zero function qualifies. The difference and product limit laws give left limits $0-0$ and $0\cdot0$. The functions' values at $1$ do not affect this test.

**(f) Yes.** The rational span contains zero and is closed under subtraction. For $u=nx$, $v=mx$, the product-to-sum identities give

$$
\begin{aligned}
2\sin u\sin v&=\cos(u-v)-\cos(u+v),\\
2\cos u\cos v&=\cos(u-v)+\cos(u+v),\\
2\sin u\cos v&=\sin(u+v)+\sin(u-v).
\end{aligned}
$$

All coefficients are rational. A negative frequency can be replaced by a nonnegative one because cosine is even and sine is odd. Distributing proves product closure for the entire span.
