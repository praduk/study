**Strategy.** Use @[Gaussian division]mt4-gaussian-division on each pair. Round the real and imaginary parts of the quotient to obtain a Gaussian integer, then subtract to get a remainder. By @[the Euclidean algorithm]mt4-euclidean-gcd, the last nonzero remainder generates the original ideal.

**The pair $85,1+13i$.** The first quotient before rounding is $85/(1+13i)=\tfrac12-\tfrac{13}{2}i$. Choosing $1-6i$ at the two ties gives

$$
\begin{aligned}
85&=(1-6i)(1+13i)+(6-7i),\\
1+13i&=(-1+i)(6-7i).
\end{aligned}
$$

The @[Gaussian norm]mt4-quadratic-integers-norm $N(a+bi)=a^2+b^2$ drops from $170$ to $85$ and the next remainder is zero. Hence $(85,1+13i)=(6-7i)$.

**The pair $47-13i,53+56i$.** Start with $53+56i$, which has the larger norm. Successive divisions give

$$
\begin{aligned}
53+56i&=(1+i)(47-13i)+(-7+22i),\\
47-13i&=(-1-2i)(-7+22i)+(-4-5i),\\
-7+22i&=(-2-3i)(-4-5i).
\end{aligned}
$$

The divisor norms decrease from $2378$ to $533$ to $41$. The last nonzero remainder is $-4-5i$. Multiplying by the unit $-1$ gives the @[associate generator]mt4-associates $4+5i$, so $(47-13i,53+56i)=(4+5i)$.
