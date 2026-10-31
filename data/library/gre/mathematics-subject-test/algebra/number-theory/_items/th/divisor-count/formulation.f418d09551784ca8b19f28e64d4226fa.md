If positive integer $n=\prod_i p_i^{e_i}$, then

$$
\tau(n)=\prod_i(e_i+1).
$$

Each divisor chooses one exponent independently from zero through $e_i$. Counting only square divisors replaces $e_i+1$ by $\lfloor e_i/2\rfloor+1$.

**Recognition cue.** Translate divisibility restrictions into independent exponent choices.

**Boundary check.** Include exponent zero, which allows divisors omitting a prime.

**Practice different uses:**

- @gre:mathematics-subject-test:algebra:number-theory:pb:divisor-count-three-sixty
- @gre:mathematics-subject-test:algebra:number-theory:pb:square-divisor-count
