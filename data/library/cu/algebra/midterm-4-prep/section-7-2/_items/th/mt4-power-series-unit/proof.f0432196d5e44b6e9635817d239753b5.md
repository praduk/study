If $a(x)$ is a @[unit]mt4-unit with inverse $b(x)$, the constant term of the @[coefficient product]mt4-power-series gives $a_0b_0=1$. In the commutative coefficient ring this makes $a_0$ a unit. Conversely put $b_0=a_0^{-1}$ and, for $k\ge1$, recursively define

$$
b_k=-a_0^{-1}\sum_{i=1}^k a_i b_{k-i}.
$$

Each new $b_k$ uses only $b_0,\ldots,b_{k-1}$, so the formula determines the coefficients successively by @[recursion on the finite coefficient list]math:set:naturals-recursion:th:natural-recursion. The constant term of $a(x)b(x)$ is $a_0b_0=1$. For $k\ge1$ the coefficient is $a_0b_k+\sum_{i=1}^k a_i b_{k-i}=0$ by construction. Hence $a(x)b(x)=1$, and commutativity gives $b(x)a(x)=1$ as well.
