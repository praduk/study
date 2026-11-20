**(a)** Evaluating $i$ at $1$ modulo $2$ respects $i^2=-1$ since $1=-1$ in $\F_2$. The resulting map $a+bi\mapsto a+b\pmod2$ is onto. Its kernel consists of pairs of equal parity, exactly $(1+i)$, since

$$
\frac{a+bi}{1+i}=\frac{a+b}{2}+\frac{b-a}{2}i.
$$

By @[the first isomorphism theorem]mt4-first-isomorphism, the quotient is $\F_2$.

**(b)** By @[the Gaussian prime classification]mt4-gaussian-primes, $q$ remains irreducible. By @[Gaussian division]mt4-gaussian-division and @[Proposition 1]mt4-euclidean-principal, the Gaussian ring is a PID. Hence $(q)$ is maximal by @[Proposition 11]mt4-pid-prime-irreducible. By @[the maximal ideal quotient criterion]mt4-maximal-quotient-field, the quotient is a field. Two Gaussian integers agree modulo $(q)$ precisely when their real and imaginary coefficients separately agree modulo $q$, giving $q^2$ elements.

**(c)** The factors $\pi,\bar\pi$ are nonassociate irreducibles by @[the Gaussian prime classification]mt4-gaussian-primes. Their principal ideals are distinct by @[the criterion for associates]mt4-associates, and both are maximal by the same PID argument. Their sum properly contains $(\pi)$, hence is $G$, so they are @[comaximal]mt4-comaximal. By @[the Chinese remainder theorem]mt4-chinese-remainder, their intersection equals their product $(\pi\bar\pi)=(p)$, and reducing modulo the two ideals induces the required ring isomorphism. The coefficient count in (b) gives $|G/(p)|=p^2$. Both factors are fields, and conjugation interchanges their defining ideals, giving an isomorphism between them. Their equal sizes therefore multiply to $p^2$, so each has size $p$.
