For prime $p$ and integer $n\ge0$,

$$
v_p(n!)=\sum_{j\ge1}\left\lfloor\frac n{p^j}\right\rfloor.
$$

Here $v_p(N)$ is the exponent of $p$ in the positive integer $N$. For factorial quotients such as binomial coefficients, subtract the corresponding exponents. Trailing decimal zeros count paired factors two and five.

**Recognition cue.** Count multiples of $p$, then extra contributions from $p^2,p^3,\ldots$.

**Boundary check.** Counting multiples of $p$ once misses repeated prime factors.

**Practice different uses:**

- @gre:mathematics-subject-test:algebra:number-theory:pb:factorial-trailing-zeros
- @gre:mathematics-subject-test:algebra:number-theory:pb:binomial-prime-exponent
