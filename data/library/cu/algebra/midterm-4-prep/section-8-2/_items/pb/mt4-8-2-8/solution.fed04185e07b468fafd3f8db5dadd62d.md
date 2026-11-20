**Strategy.** To prove the localization is a PID, check that it is a domain and that every ideal has a single generator. For the second check, intersect an ideal with $R$ and clear denominators to recover the whole ideal from this intersection.

**Embed the localization in a field.** Write $S=D^{-1}R$. Send $r/d\in S$ to the same fraction in the @[fraction field]mt4-field-of-fractions of $R$. The @[localization rules]mt4-ring-of-fractions agree with the fraction-field rules for sums, products, and equality by cross multiplication, so this is an injective ring map. For any $d\in D$, the fraction $d/d$ is the identity. Thus $S$ contains $1\ne0$ and inherits the zero-product property of the field, making it an @[integral domain]mt4-integral-domain.

**Get a generator in $R$.** Identify $R$ with its image under the @[canonical embedding]mt4-fractions-embedding. Given any ideal $J$ of $S$, its intersection $I=J\cap R$ is an @[ideal]mt4-ideal of $R$. It contains $0$, and differences and multiples by elements of $R$ stay in both $R$ and $J$. By the @[PID hypothesis]mt4-pid, $I=(a)$ for some $a\in R$.

**Show $J=aS$.** If $r/d\in J$, multiplying by $d$ gives $r\in J\cap R=(a)$. Write $r=at$ with $t\in R$. Then $r/d=a(t/d)\in aS$. Conversely $a\in I\subseteq J$, so every multiple of $a$ in $S$ belongs to $J$. Thus $a$ generates $J$, including when $J=(0)$.
