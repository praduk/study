By @[nilpotence]mt4-nilpotent, choose the least $n\ge1$ with $x^n=0$.

**(a)** If $x\ne0$, then $n\ge2$ and $x^{n-1}\ne0$. The equality $x x^{n-1}=0$ makes $x$ a @[zero divisor]mt4-zero-divisor.

**(b)** Commutativity gives $(rx)^n=r^n x^n=0$.

**(c)** Set $v=\sum_{j=0}^{n-1}(-x)^j$. Telescoping gives $(1+x)v=v(1+x)=1-(-x)^n=1$, so $v$ is the inverse required by the @[definition of a unit]mt4-unit.

**(d)** Factor $u+x=u(1+u^{-1}x)$. The element $u^{-1}x$ is nilpotent by (b), so the second factor is a unit by (c). Their product is a unit.
