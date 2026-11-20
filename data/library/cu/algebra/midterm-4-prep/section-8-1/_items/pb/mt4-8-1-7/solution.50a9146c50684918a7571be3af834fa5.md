Use @[Gaussian division]mt4-gaussian-division with $N(a+bi)=a^2+b^2$. For the first pair,

$$
\begin{aligned}
85&=(1-6i)(1+13i)+(6-7i),\\
1+13i&=(-1+i)(6-7i).
\end{aligned}
$$

The nonzero divisor norms decrease from $170$ to $85$. By @[the Euclidean algorithm]mt4-euclidean-gcd, the ideal is $(6-7i)$.

For the second pair start with the larger norm. The divisions are

$$
\begin{aligned}
53+56i&=(1+i)(47-13i)+(-7+22i),\\
47-13i&=(-1-2i)(-7+22i)+(-4-5i),\\
-7+22i&=(-2-3i)(-4-5i).
\end{aligned}
$$

The divisor norms are $2378,533,41$. Hence a generator is $-4-5i$, equivalently $4+5i$.
