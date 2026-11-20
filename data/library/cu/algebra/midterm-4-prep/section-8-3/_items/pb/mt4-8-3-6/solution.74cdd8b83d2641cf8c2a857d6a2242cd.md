**(a)** Evaluating $i$ at $1$ modulo $2$ respects $i^2=-1$ since $1=-1$ in $\F_2$. The resulting @[ring homomorphism]mt4-ring-homomorphism $a+bi\mapsto a+b\pmod2$ is onto since it hits $0,1$. Its kernel consists of pairs of equal parity, exactly $(1+i)$, since

$$
\frac{a+bi}{1+i}=\frac{a+b}{2}+\frac{b-a}{2}i.
$$

By @[the first isomorphism theorem]mt4-first-isomorphism, the quotient is $\F_2$.

**(b)** By @[the Gaussian prime classification]mt4-gaussian-primes, $q$ remains irreducible. By @[Gaussian division]mt4-gaussian-division and @[Proposition 1]mt4-euclidean-principal, the Gaussian ring is a PID. Hence $(q)$ is maximal by @[Proposition 11]mt4-pid-prime-irreducible. By @[the maximal ideal quotient criterion]mt4-maximal-quotient-field, the quotient is a field. Two @[quotient classes]mt4-quotient-ring agree precisely when their difference is a multiple of $q$, that is, when their real and imaginary coefficients separately agree modulo $q$. There are $q$ choices for each coordinate, giving $q^2$ classes by @[the multiplication principle]gre:mathematics-subject-test:discrete-mathematics:th:multiplication-counting.

**(c)** The factors $\pi,\bar\pi$ are nonassociate irreducibles by @[the Gaussian prime classification]mt4-gaussian-primes. Their principal ideals are distinct by @[the criterion for associates]mt4-associates, and both are maximal by the same PID argument. Neither maximal ideal can properly contain the other. Thus their @[sum]mt4-ideal-sum-product strictly contains $(\pi)$ and must be $G$ by @[maximality]mt4-maximal-ideal. This proves they are @[comaximal]mt4-comaximal. By @[the Chinese remainder theorem]mt4-chinese-remainder, their intersection equals their product $(\pi\bar\pi)=(p)$, and reducing modulo the two ideals induces the required ring isomorphism. The coefficient count in (b) gives $|G/(p)|=p^2$. Both factors are fields by maximality. Conjugation sends the ideal $(\pi)$ onto $(\bar\pi)$, so $z+(\pi)\mapsto\bar z+(\bar\pi)$ is well defined, preserves sums and products, and has conjugation as its inverse. The two factors have the same size $h$. Their @[direct product]mt4-direct-product-rings has $h^2=p^2$ elements, so $h=p$.
