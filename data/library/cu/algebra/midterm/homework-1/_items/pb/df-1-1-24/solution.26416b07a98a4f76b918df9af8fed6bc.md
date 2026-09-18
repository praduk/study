The case $n=0$ is immediate. Inductively, if the formula holds for $n\ge0$, then

$$
(ab)^{n+1}=a^nb^nab=a^{n+1}b^{n+1},
$$

because $b^na=ab^n$ (itself obtained by induction from $ba=ab$).
For $n=-m<0$,

$$
(ab)^{-m}=((ab)^{-1})^m=(b^{-1}a^{-1})^m=b^{-m}a^{-m}=a^{-m}b^{-m}.
$$

Here $a^{-1}$ and $b^{-1}$ commute, as follows by inverting $ab=ba$.

**Technique:** positive induction, then handle zero and negative exponents separately. Without commutativity the claim fails, for example for $(12),(23)\in S_3$ at $n=2$.
