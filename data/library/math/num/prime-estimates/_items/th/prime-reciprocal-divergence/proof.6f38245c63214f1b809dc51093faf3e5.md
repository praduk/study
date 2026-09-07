Assume it converges. Choose $K$ so large that $\sum_{p>K}1/p<1/2$, and list the finitely many primes at most $K$. The sum of reciprocals of integers all of whose prime factors lie on this finite list is the finite product $C=\prod_{p\le K}(1-1/p)^{-1}$. Among integers up to $N$, every other integer is divisible by a prime $p>K$, so its reciprocal sum is at most

$$
\sum_{K<p\le N}\frac1p H_{\lfloor N/p\rfloor}\le\frac12 H_N,
$$

where $H_N=\sum_{j=1}^N1/j$. Hence $H_N\le C+H_N/2$, giving $H_N\le2C$ for all $N$. But grouping harmonic terms between successive powers of $2$ contributes at least $1/2$ per group, so $H_N$ is unbounded. Contradiction.
