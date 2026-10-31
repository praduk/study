For integers $a,b$ and $n\ge1$, set $d=\gcd(a,n)$. The congruence $ax\equiv b\pmod n$ is solvable iff $d\mid b$. When solvable, it has exactly $d$ distinct classes modulo $n$. Divide $a,b,n$ by $d$, solve the resulting invertible congruence, then lift the answer to the original modulus.

**Recognition cue.** A gcd determines both existence and the number of solutions before solving.

**Boundary check.** After reducing the modulus, remember to lift all classes.

**Practice different uses:**

- @gre:mathematics-subject-test:algebra:number-theory:pb:linear-congruence-solution-count
- @gre:mathematics-subject-test:algebra:number-theory:pb:linear-congruence-list
