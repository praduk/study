For positive integer $n=\prod_i p_i^{e_i}$,

$$
\varphi(n)=n\prod_{p\mid n}\left(1-\frac1p\right).
$$

It counts the residue classes coprime to $n$; use each distinct prime once. The empty product gives $\varphi(1)=1$. For a prime power, $\varphi(p^e)=p^e-p^{e-1}$.

**Recognition cue.** Factor the modulus and remove multiples of its distinct primes.

**Boundary check.** Do not repeat a prime's factor once per exponent.

**Practice different uses:**

- @gre:mathematics-subject-test:algebra:number-theory:pb:euler-phi-eighty-four
- @gre:mathematics-subject-test:algebra:number-theory:pb:totient-prime-power
