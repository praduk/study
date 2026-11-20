**Strategy.** First check the zero polynomial against the definition. For a nonzero polynomial $p$, a scalar that kills $p$ gives one direction immediately. For the converse, choose a polynomial of least degree that kills $p$ and show that its leading coefficient already kills $p$.

**The zero polynomial is exceptional.** The @[zero-divisor definition]mt4-zero-divisor excludes zero. For example, in $\Z[x]$ the scalar $1$ kills $p=0$, although $0$ is not a zero divisor. From now on assume $p\ne0$.

**A nonzero scalar annihilator makes $p$ a zero divisor.** If $b\ne0$ in $R$ and $bp=0$, then the constant polynomial $b$ is a nonzero element of $R[x]$ whose product with $p$ vanishes.

**Conversely, choose an annihilator of least degree.** Suppose $p=\sum_{j=0}^n a_jx^j$ is a zero divisor. Its @[annihilator]mt4-annihilator contains a nonzero polynomial. By @[well-ordering]math:set:orders-well-orders:df:well-order, choose such a $g$ of least degree $m$. Let $b_m\ne0$ be its leading coefficient. We need $a_k b_m=0$ for every $k$.

**Remove one coefficient of $p$ at a time.** Work downwards from $k=n$ to $k=0$ by @[induction]math:set:naturals-recursion:th:natural-induction. Write $p_k=\sum_{j=0}^k a_jx^j$. At the start of each step, $p_kg=0$. This holds initially because $p_n=p$.

1. The @[polynomial coefficient formula]mt4-polynomial-ring gives $a_kb_m=0$ by comparing coefficients of $x^{k+m}$ in $p_kg=0$.
2. Consequently $a_kg$ is zero or has degree less than $m$. It still annihilates $p$, since $(a_kg)p=a_k(gp)=0$. By minimality of $m$, it must be zero.
3. If $k>0$, subtract $a_kx^kg=0$ from $p_kg=0$ to obtain $p_{k-1}g=0$. This establishes the starting equation for the next step.

The first line of each step gives $a_kb_m=0$ for that $k$. Thus every coefficient of $b_mp$ is zero. The element $b_m\in R$ is the required nonzero scalar.
