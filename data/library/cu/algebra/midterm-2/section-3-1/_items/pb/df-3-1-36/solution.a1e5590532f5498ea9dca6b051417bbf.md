Let $xZ(G)$ generate $G/Z(G)$. This includes the trivial quotient: then we may take $x=1$. Every $g\in G$ has $gZ(G)=x^aZ(G)$ for some integer $a$. Equality of these cosets means $x^{-a}g\in Z(G)$, so $g=x^az$ for some $z\in Z(G)$.

Take arbitrary $g=x^az$ and $h=x^bw$, with $z,w$ central. Central elements commute with $x$ and with one another, and powers of the same element commute. Therefore

$$
gh=x^azx^bw=x^{a+b}zw=x^{b+a}wz=x^bwx^az=hg.
$$

Since $g,h$ were arbitrary, $G$ is abelian.

**Boundary check.** An abelian quotient by an arbitrary normal subgroup does not imply $G$ is abelian: $S_3/A_3\cong C_2$. The argument works here because the kernel is the center, so the extra factors $z,w$ commute with everything.

**Technique:** equality in a quotient gives a normal form modulo the kernel. Identify exactly what property of the kernel allows the next calculation.

**Foundations:** @cu:algebra:midterm-2:definitions:df:normal-quotient, @cu:algebra:midterm-2:theorems:th:commutator-criterion.
