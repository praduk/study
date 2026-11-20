**Strategy.** Start with the first power of $x$ that vanishes. The previous power detects a zero divisor, and the vanishing power makes a finite geometric sum into an inverse. To handle $u+x$, factor out the unit $u$.

**(a) Find a nonzero element killed by $x$.** By @[nilpotence]mt4-nilpotent and @[well-ordering]math:set:orders-well-orders:df:well-order, there is a least $n\ge1$ with $x^n=0$. If $x=0$, the first alternative holds. If $x\ne0$, then $n\ge2$ and $x^{n-1}\ne0$. Since $x\,x^{n-1}=0$, $x$ is a @[zero divisor]mt4-zero-divisor.

**(b) Show that $rx$ is nilpotent.** For any $r\in R$, commutativity allows us to regroup the factors as $(rx)^n=r^nx^n=0$.

**(c) Construct an inverse for $1+x$.** Let $v=\sum_{j=0}^{n-1}(-x)^j$. In $(1+x)v=(1-(-x))v$, the intermediate powers cancel in pairs. The @[ring sign rules]mt4-ring-arithmetic give

$$
(1+x)v=1-(-x)^n=1.
$$

Commutativity also gives $v(1+x)=1$. Thus $v$ is a two-sided inverse and $1+x$ is a @[unit]mt4-unit.

**(d) Reduce $u+x$ to part (c).** Since $u$ is a unit, write $u+x=u(1+u^{-1}x)$. By (b), $u^{-1}x$ is nilpotent, so by (c), $1+u^{-1}x$ is a unit. The @[group of units]mt4-unit is closed under multiplication, so $u+x$ is a unit.
