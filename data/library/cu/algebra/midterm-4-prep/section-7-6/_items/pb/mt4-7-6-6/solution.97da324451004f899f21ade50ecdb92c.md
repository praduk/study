Write $f_i=\sum_{j=0}^{d}a_{ij}x^j$ using @[the coefficient representation of a polynomial]mt4-polynomial-ring. By @[the comaximality criterion for integer ideals]mt4-comaximal the integer ideals $(n_i)$ are pairwise comaximal. For each $j$, apply @[the Chinese remainder theorem]mt4-chinese-remainder in $\Z$ to choose $c_j$ such that $c_j\equiv a_{ij}\pmod{n_i}$ for all $i$.

When all moduli are nonzero, adding any multiple of $N=|n_1\cdots n_k|$ preserves the simultaneous congruences. Thus if $c_d=0$ we may replace it by $N$, and $f=\sum_{j=0}^d c_jx^j$ then has degree exactly $d$. When the $f_i$ are monic, take $c_d=1$ from the start.

If a zero modulus $n_s$ is allowed, congruence modulo $(0)$ is equality, and pairwise coprimality forces every other modulus to be $\pm1$. Then $f=f_s$ has all the required properties.
