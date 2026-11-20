**Strategy.** Solve one integer congruence problem for each coefficient. Then check the leading coefficient separately so that the resulting polynomial has degree exactly $d$ and is monic when requested.

**1. Handle a zero modulus.** If $n_s=0$, congruence modulo $(0)$ forces equality with $f_s$. Every other modulus is $\pm1$, since $\gcd(0,n_i)=|n_i|=1$ for $i\ne s$. Those congruences impose no restriction, so $f=f_s$ has all the required properties. Now assume every modulus is nonzero.

**2. Choose each coefficient.** Use @[the coefficient representation of a polynomial]mt4-polynomial-ring to write $f_i=\sum_{j=0}^d a_{ij}x^j$. The moduli are pairwise @[coprime]math:num:divisibility:df:divisibility-gcd. By @[Bézout’s identity]math:num:divisibility:th:bezout-euclid, their ideals are pairwise @[comaximal]mt4-comaximal, since $(n_i)+(n_h)=\Z$ whenever $i\ne h$.

For each fixed $j$, @[the Chinese remainder theorem]mt4-chinese-remainder gives an integer $c_j$ with $c_j-a_{ij}\in(n_i)$ for every $i$. Thus $f=\sum_{j=0}^d c_jx^j$ satisfies every required @[coefficient congruence]mt4-quotient-ring.

**3. Ensure degree $d$ and handle the monic case.** If $c_d=0$, replace it by $N=|n_1\cdots n_k|$. This number is positive and divisible by every $n_i$, so the leading coefficient becomes nonzero while keeping the same residues. Hence $\deg f=d$. If all the $f_i$ are monic, their leading coefficients are all $1$, so choose $c_d=1$ from the start. Then $f$ is monic of degree $d$.
