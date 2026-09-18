(a) The sum of $a+b\sqrt2$ and $c+d\sqrt2$ is $(a+c)+(b+d)\sqrt2$, which lies in $G$. The identity is $0=0+0\sqrt2$, and the additive inverse is $-a-b\sqrt2$. Associativity is inherited from $\R$.

(b) Products have the form

$$
(a+b\sqrt2)(c+d\sqrt2)=(ac+2bd)+(ad+bc)\sqrt2.
$$

The product of two nonzero real numbers is nonzero. The identity is $1$, and associativity is inherited from $\R$. For $a+b\sqrt2\ne0$,

$$
(a+b\sqrt2)^{-1}=\frac{a-b\sqrt2}{a^2-2b^2}.
$$

The denominator is nonzero: if $b=0$ this follows from $a\ne0$; otherwise its vanishing would imply $(a/b)^2=2$, contradicting the irrationality of $\sqrt2$. Both coefficients are rational, so the inverse belongs to $G\setminus\{0\}$.

For completeness, if $\sqrt2=u/v$ in lowest terms with integers $v\ne0$, then $u^2=2v^2$ forces $u$ even, and then $v$ even, a contradiction.

**Technique:** inherit associativity from an ambient group; explicitly verify closure, identity, and inverses; rationalize using a conjugate.
