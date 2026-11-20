**Strategy.** In a UFD, divisibility can be checked one prime at a time. At each prime, choose the smallest exponent large enough for *both* $a$ and $b$ to divide the proposed lcm.

**Construct the candidate.** The irreducibles in a UFD are @[prime]mt4-irreducible-prime. Take one @[prime element]mt4-prime-element $p$ from each @[associate class]mt4-associates appearing in $ab$. By @[unique factorization]mt4-ufd the exponents $e_p$ in $a$ and $f_p$ in $b$ are well defined, taking zero when $p$ is absent. Set

$$
L=\prod_p p^{\max(e_p,f_p)}.
$$

**Check the two lcm conditions.**

- **Common multiple.** At each $p$, the exponent of $L$ is at least $e_p$ and at least $f_p$. By the @[UFD divisibility test]mt4-ufd-gcd, $a\mid L$ and $b\mid L$.
- **Divides every common multiple.** If $m\ne0$ is divisible by both inputs, its exponent at each listed $p$ is at least $\max(e_p,f_p)$. Thus $L\mid m$ by the same test. Also $L\mid0$.

This proves the @[lcm property]mt4-lcm. If both inputs are units, the product is empty and gives $L=1$. Any two lcms divide each other, hence generate the same ideal and differ by a unit by @[Exercise 7.4.8]mt4-7-4-8.
