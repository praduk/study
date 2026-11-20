**Coefficients in a field.** In a @[formal power series]mt4-power-series the exponents are nonnegative. If nonzero power series first have nonzero coefficients in degrees $i,j$, their product first has a nonzero coefficient in degree $i+j$, namely the product of those two coefficients. That product is nonzero since @[a field is an integral domain]gre:mathematics-subject-test:abstract-algebra:th:field-domain. Thus $F[[x]]$ is a domain.

By @[Exercise 7.2.5]mt4-7-2-5, the @[Laurent series]mt4-laurent-series form a field containing $F[[x]]$. Indeed, a nonzero series in $F((x))$ is $x^m u(x)$, with $u$ invertible by @[the power series unit criterion]mt4-power-series-unit, and has inverse $x^{-m}u^{-1}$. Every $L\in F((x))$ has a lower bound on its exponents. Choose $k\ge0$ so that $x^kL\in F[[x]]$. Then $L=(x^kL)/x^k$ is a quotient of two power series, and @[the fraction field characterization]mt4-fraction-subfield identifies $\operatorname{Frac}(F[[x]])$ with all of $F((x))$.

**Integer coefficients.** Now $\Z[[x]]$ embeds coefficientwise in $\Q((x))$, a field, so it is a domain. Every nonzero denominator becomes invertible there. Thus its @[field of fractions]mt4-field-of-fractions embeds in $\Q((x))$ by @[the extension theorem for fractions]mt4-fractions-embedding. To see that the image is proper, consider the formal series

$$
E(x)=\sum_{n\ge0}\frac{x^n}{n!}.
$$

If it were a fraction $f/g$ with $f,g\in\Z[[x]]$ and $g\ne0$, then $gE=f$. Let $m$ be the first index with $g_m\ne0$. By @[the infinitude of primes]math:num:prime-estimates:th:infinitely-many-primes, choose a prime $p>|g_m|$. The power series product rule in degree $m+p$, multiplied by $p!$, gives

$$
p!f_{m+p}=g_m+\sum_{j=1}^p g_{m+j}\frac{p!}{(p-j)!}.
$$

For every $1\le j\le p$, the integer $p!/(p-j)!$ has $p$ as a factor. Reducing both sides modulo $p$ therefore gives $g_m\equiv0\pmod p$, contrary to $0<|g_m|<p$. This proves that $E(x)$ lies outside the image.
