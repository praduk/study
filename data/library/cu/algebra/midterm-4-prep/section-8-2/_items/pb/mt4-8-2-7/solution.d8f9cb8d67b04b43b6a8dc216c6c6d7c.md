**Strategy.** A generator of $(a,b)$ has two useful properties. It divides $a$ and $b$, and it is a linear combination of them. Use these to prove (a), then apply the two-generator result repeatedly in (b) and cancel the common factor in (c).

**(a) Prove the equivalence.**

- **From Bézout to a gcd identity.** In a @[Bézout domain]mt4-bezout-domain write $(a,b)=(d)$. For $a,b$ not both zero, the @[gcd generator criterion]mt4-gcd-generated-pair shows $d$ is a gcd. Since $d\in(a,b)$, it has the required form $ax+by$.
- **From a gcd identity to Bézout.** Suppose a gcd $d$ satisfies $d=ax+by$. Because $d$ divides $a$ and $b$, we have $(a,b)\subseteq(d)$. The identity places $d$ in $(a,b)$, giving the reverse inclusion. Thus $(a,b)$ is principal. For $a=b=0$, the ideal is $(0)$ and the identity holds with the stated convention $d=0$.

**(b) Reduce a finite list to one generator.** By the definition of a @[generated ideal]mt4-principal-ideal, the empty list generates $(0)$ and a one-element list already gives a principal ideal. If the first $n$ generators give $(d)$, adjoining a generator $c$ gives $(d,c)$, which is principal by the Bézout property. @[Induction]math:set:naturals-recursion:th:natural-induction covers every finite list.

**(c) Reduce a fraction to relatively prime terms.** Take $a/b$ in the @[fraction field]mt4-field-of-fractions, with $b\ne0$. Choose a gcd $d=ax+by$ as in (a), and write $a=da'$, $b=db'$. Since $b\ne0$, both $d$ and $b'$ are nonzero and $a/b=a'/b'$.

It remains to show the new numerator and denominator are relatively prime. Substitution in the gcd identity gives $d=d(a'x+b'y)$. By @[cancellation]mt4-cancellation, $1=a'x+b'y$. Any common divisor of $a',b'$ divides the right-hand side, hence divides $1$. Since $1$ divides both, this is precisely @[relative primality]mt4-divisibility-gcd.
