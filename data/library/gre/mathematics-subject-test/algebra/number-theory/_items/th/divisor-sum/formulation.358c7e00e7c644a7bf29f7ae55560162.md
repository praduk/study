For positive integer $n=\prod_i p_i^{e_i}$,

$$
\sigma(n)=\prod_i(1+p_i+\cdots+p_i^{e_i})=\prod_i\frac{p_i^{e_i+1}-1}{p_i-1}.
$$

Multiplication enumerates each divisor once. The sum of proper positive divisors is $\sigma(n)-n$.

**Recognition cue.** A product of finite geometric sums avoids listing every divisor.

**Boundary check.** A proper-divisor sum excludes $n$ but includes one for $n>1$.

**Practice different uses:**

- @gre:mathematics-subject-test:algebra:number-theory:pb:divisor-sum-sixty
- @gre:mathematics-subject-test:algebra:number-theory:pb:perfect-number-check
