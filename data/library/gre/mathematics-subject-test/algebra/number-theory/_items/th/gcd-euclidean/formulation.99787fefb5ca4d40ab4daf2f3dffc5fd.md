For integers $a,b$, $a\mid b$ means $b=ak$ for an integer $k$. For $a,b$ not both zero, take $\gcd(a,b)>0$. If $a=qb+r$, then $\gcd(a,b)=\gcd(b,r)$; repeated division gives the last nonzero remainder. For positive $a,b$, $\gcd(a,b)\lcm(a,b)=ab$.

**Recognition cue.** Replace a large pair by a small remainder pair.

**Boundary check.** A gcd is positive even when the original integers have signs.

**Practice different uses:**

- @gre:mathematics-subject-test:algebra:number-theory:pb:gcd-large-pair
- @gre:mathematics-subject-test:algebra:number-theory:pb:gcd-lcm-product
