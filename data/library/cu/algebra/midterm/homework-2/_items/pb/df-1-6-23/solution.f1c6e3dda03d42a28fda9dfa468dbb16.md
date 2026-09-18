Define $f(x)=x^{-1}\alpha(x)$. If $f(x)=f(y)$, multiplication on the left by $y$ and on the right by $\alpha(x)^{-1}$ gives

$$
yx^{-1}=\alpha(y)\alpha(x)^{-1}=\alpha(yx^{-1}).
$$

The fixed-point hypothesis forces $yx^{-1}=1$, so $x=y$. Thus $f$ is injective and, since $G$ is finite, surjective.
For $g=x^{-1}\alpha(x)$,

$$
\alpha(g)=\alpha(x)^{-1}\alpha^2(x)=\alpha(x)^{-1}x=g^{-1}.
$$

Surjectivity makes this true for every $g\in G$. Consequently

$$
b^{-1}a^{-1}=(ab)^{-1}=\alpha(ab)=\alpha(a)\alpha(b)=a^{-1}b^{-1}.
$$

Taking inverses gives $ab=ba$.

**Technique:** construct an injective self-map, use finiteness for surjectivity, then compare an automorphism with inversion.
