For integers $a,b$ not both zero, there exist integers $x,y$ with

$$
ax+by=\gcd(a,b).
$$

Back-substitution in the Euclidean algorithm finds them. Every integer combination of $a,b$ is a multiple of the gcd, so an identity $ax+by=1$ certifies coprimality.

**Recognition cue.** A gcd computation can also produce a modular inverse or impossibility certificate.

**Boundary check.** A random integer combination need not equal the gcd; verify the claimed value.

**Practice different uses:**

- @gre:mathematics-subject-test:algebra:number-theory:pb:bezout-two-hundred-fifty-two
- @gre:mathematics-subject-test:algebra:number-theory:pb:coprime-consecutive-expressions
