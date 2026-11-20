**Representatives.** Divide $g$ by $f$ using @[polynomial division]mt4-division-polynomials. This gives $g=qf+r$ with $r=0$ or $\deg r<n$. Since $g-r\in(f)$, the two polynomials give the same @[quotient class]mt4-quotient-ring. If $s$ is another such representative, $r-s$ belongs to the @[principal ideal]mt4-principal-ideal $(f)$. Every nonzero multiple of $f$ has degree at least $n$ by @[the degree formula]mt4-polynomial-domains, whereas $r-s$ is zero or has degree less than $n$. Hence $r=s$.

**Basis.** Scalars act on the quotient by $c\bar g=\overline{cg}$. This is well defined because $g-h\in(f)$ implies $c(g-h)\in(f)$, and the @[vector space laws]math:algebra:linear-foundations:df:vector-space follow from addition and multiplication in $F[x]$. The unique remainder of each class gives a unique expression

$$
c_0\bar 1+c_1\bar x+\cdots+c_{n-1}\overline{x^{n-1}},\qquad c_i\in F.
$$

Existence gives spanning. Uniqueness applied to the zero class forces every coefficient in a zero relation to vanish. Thus these $n$ classes are linearly independent and form a @[basis]math:algebra:linear-foundations:df:basis-dimension. The dimension is $n$.
