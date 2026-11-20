By @[nilpotence]mt4-nilpotent the set of positive exponents $n$ with $x^n=0$ is nonempty. Choose its least member using the @[well-ordering]math:set:orders-well-orders:df:well-order of the positive integers.

**(a)** If $x\ne0$, then $n\ge2$ and $x^{n-1}\ne0$. The equality $x x^{n-1}=0$ makes $x$ a @[zero divisor]mt4-zero-divisor.

**(b)** Commutativity gives $(rx)^n=r^n x^n=0$.

**(c)** Set $v=\sum_{j=0}^{n-1}(-x)^j$. On multiplying by $1+x=1-(-x)$, the terms of degrees $1$ through $n-1$ cancel in pairs. The @[ring sign rules]mt4-ring-arithmetic therefore give $(1+x)v=v(1+x)=1-(-x)^n=1$, so $v$ is the inverse required by the @[definition of a unit]mt4-unit.

**(d)** Factor $u+x=u(1+u^{-1}x)$. The element $u^{-1}x$ is nilpotent by (b), so the second factor is a unit by (c). Their product belongs to the @[group of units]mt4-unit.
