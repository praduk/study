Let $R$ be commutative. Let $D\subseteq R$ be nonempty and closed under multiplication, with every element of $D$ nonzero and not a zero divisor. The **ring of fractions** $D^{-1}R$ consists of classes $r/d$ of pairs $(r,d)\in R\times D$, where $r/d=s/e$ means $re=sd$. Its operations are

$$
\frac r d+\frac s e=\frac{re+sd}{de},\qquad
\frac r d\frac s e=\frac{rs}{de}.
$$

Its identity is $d/d$ for any $d\in D$. Under the @[canonical embedding]mt4-fractions-embedding $r\mapsto rd/d$, the elements of $D$ become units. If $1\in D$, this inclusion is $r\mapsto r/1$.

**Why the construction works.** Cross multiplication defines an @[equivalence relation]math:set:relations-functions:df:equivalence-relation. Reflexivity and symmetry follow from equality in $R$. For transitivity, suppose $re=sd$ and $sf=te$. Then $ref=sdf=tde$. The middle denominator $e$ is not a zero divisor, so @[cancelling it]mt4-cancellation gives $rf=td$.

Multiplying a numerator and its denominator by the same $u\in D$ preserves the class. Conversely, equivalent representatives $r/d$ and $s/e$ become literally the same pair at denominator $de$, since $re=sd$. In the two operation formulas above, rescaling one input by $u$ rescales the output numerator and denominator by $u$ as well. Passing to common representatives therefore shows that both operations are well defined.

The zero class is $0/d$, the negative of $r/d$ is $(-r)/d$, and multiplication by $e/e$ fixes every fraction. The associative, commutative, and distributive laws follow by taking common denominators and applying the corresponding @[ring laws]mt4-ring to the numerators.
