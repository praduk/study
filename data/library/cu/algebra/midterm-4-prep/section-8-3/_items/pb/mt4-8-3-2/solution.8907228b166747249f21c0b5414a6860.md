Take one @[prime element]mt4-prime-element $p$ from each associate class appearing in $ab$. By @[unique factorization]mt4-ufd its exponents in $a$ and $b$ are well defined. Call them $e_p$ and $f_p$, using zero for absence. Set

$$
L=\prod_p p^{\max(e_p,f_p)}.
$$

The divisibility test of @[Proposition 13]mt4-ufd-gcd shows $a\mid L$ and $b\mid L$. Any nonzero common multiple has exponent at least $\max(e_p,f_p)$ at each listed prime, so is divisible by $L$. Zero too is divisible by $L$. This proves @[the lcm property]mt4-lcm, including the case of two units where the product is empty and $L=1$. All lcms are associates.
