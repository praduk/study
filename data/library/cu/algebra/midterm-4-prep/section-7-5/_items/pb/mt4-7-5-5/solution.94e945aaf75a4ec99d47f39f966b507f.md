**Strategy.** Over $F$, show that Laurent series form a field and that each one is a fraction of power series. Over $\Z$, embed the fraction field into $\Q((x))$, then exhibit a rational-coefficient series that cannot be such a fraction.

**1. Put $F[[x]]$ inside a field.** A @[formal power series]mt4-power-series has only nonnegative exponents. If two nonzero series first have nonzero coefficients in degrees $i,j$, the coefficient in degree $i+j$ of their product is the product of those first coefficients. It is nonzero since @[a field is an integral domain]gre:mathematics-subject-test:abstract-algebra:th:field-domain. Thus $F[[x]]$ is a domain.

The @[Laurent series]mt4-laurent-series form a field containing $F[[x]]$ by @[Exercise 7.2.5]mt4-7-2-5. In fact, for any nonzero Laurent series, factor out its lowest power of $x$ to write it as $x^m u(x)$ with $u(0)\ne0$. By @[the power series unit criterion]mt4-power-series-unit, $u$ is invertible in $F[[x]]$, so the Laurent series has inverse $x^{-m}u^{-1}$.

**2. Express every Laurent series as a fraction.** For $L\in F((x))$, choose $k\ge0$ so that shifting the exponents by $k$ makes them all nonnegative. Then $x^kL\in F[[x]]$ and $L=(x^kL)/x^k$. By @[the fraction field characterization]mt4-fraction-subfield, this identifies $\operatorname{Frac}(F[[x]])$ with $F((x))$.

**3. Embed the fractions of integer power series.** Coefficientwise inclusion puts $\Z[[x]]$ inside the field $\Q((x))$, so $\Z[[x]]$ is a domain. Every nonzero denominator becomes invertible there. By @[the extension theorem for fractions]mt4-fractions-embedding, its @[field of fractions]mt4-field-of-fractions embeds in $\Q((x))$ by $f/g\mapsto fg^{-1}$.

**4. Find a series outside the image.** Consider $E(x)=\sum_{n\ge0}x^n/n!$ in $\Q((x))$. If $E=f/g$ with $f,g\in\Z[[x]]$ and $g\ne0$, then $gE=f$. Write $f_j,g_j$ for their coefficients of $x^j$. Let $m$ be the first index with $g_m\ne0$. By @[the infinitude of primes]math:num:prime-estimates:th:infinitely-many-primes, choose a prime $p>|g_m|$.

Compare the coefficients of $x^{m+p}$ in $gE=f$ and multiply by $p!$. Since all $g_i$ with $i<m$ vanish, this gives

$$
p!f_{m+p}=g_m+\sum_{j=1}^{p}g_{m+j}\frac{p!}{(p-j)!}.
$$

The left side is divisible by $p$. Every term of the sum is also divisible by $p$, because $p!/(p-j)!$ contains the factor $p$ when $j\ge1$. Hence $p$ divides $g_m$, which contradicts $0<|g_m|<p$. Therefore $E$ lies outside the image and the inclusion is proper.
