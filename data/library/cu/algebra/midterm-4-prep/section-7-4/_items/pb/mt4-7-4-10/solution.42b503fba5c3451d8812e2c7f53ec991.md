**Strategy.** The ring already has commutative multiplication and $1\ne0$. To prove it is an @[integral domain]mt4-integral-domain, rule out a product of two nonzero elements that equals zero.

**Use primality on a zero product.** Suppose $a,b\ne0$ and $ab=0$. Then $a$ and $b$ are both @[zero divisors]mt4-zero-divisor, since each annihilates the other. Every @[ideal]mt4-ideal contains $0$, so $ab\in P$. By @[primality]mt4-prime-ideal, at least one of $a,b$ lies in $P$. This puts a zero divisor in $P$, contradicting the hypothesis. Hence every zero product has a zero factor, as required.
