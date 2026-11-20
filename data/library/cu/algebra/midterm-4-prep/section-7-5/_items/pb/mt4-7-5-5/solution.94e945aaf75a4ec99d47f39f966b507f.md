By @[the definition of a power series]mt4-power-series and @[that of a Laurent series]mt4-laurent-series, a power series has only nonnegative exponents, while a Laurent series may have finitely many negative exponents. The least nonzero coefficients of two nonzero series multiply to give the least nonzero coefficient of their product. Over $F$ this proves $F[[x]]$ is a domain. Every nonzero Laurent series is $x^m u(x)$, where $m\in\Z$ and $u\in F[[x]]$ has nonzero constant coefficient. By @[the power series unit criterion]mt4-power-series-unit this $u$ is a unit. The Laurent series has inverse $x^{-m}u^{-1}$. Thus $F((x))$ is a field containing $F[[x]]$. Every Laurent series $L$ is $(x^k L)/x^k$ with $k\ge0$ chosen to clear its negative exponents. By @[the fraction field characterization]mt4-fraction-subfield, these fractions give all of $F((x))$.

The coefficient inclusion $\Z[[x]]\subseteq\Q((x))$ embeds its @[field of fractions]mt4-field-of-fractions there by @[the extension theorem for fractions]mt4-fractions-embedding. To prove strictness take the formal series

$$
E(x)=\sum_{n\ge0}\frac{x^n}{n!}.
$$

Suppose $gE=f$ with $f,g\in\Z[[x]]$ and $g\ne0$. Write $m$ for the least index with $g_m\ne0$, and take a prime $p>|g_m|$. Comparing the coefficient of $x^{m+p}$ and multiplying by $p!$ gives

$$
p!f_{m+p}=g_m+\sum_{j=1}^p g_{m+j}\frac{p!}{(p-j)!}.
$$

The left side and every term of the sum are divisible by $p$. This would force $p\mid g_m$, impossible. Hence $E\in\Q((x))$ lies outside the embedded fraction field.
