Let $R$ be a @[commutative ring]mt4-ring with $1$.

Prove that $p(x)$ is a @[zero divisor]mt4-zero-divisor in $R[x]$ if and only if there is a nonzero $b\in R$ such that $bp(x)=0$.

 
Let $p(x)=a_nx^n+a_{n-1}x^{n-1}+\cdots+a_1x+a_0$ be an element of the @[polynomial ring]mt4-polynomial-ring $R[x]$.

-----
$\impliedby$

Let $p\neq 0$.  Suppose there exists a nonzero $b\in R$ such that $bp(x)=0$.  $b\in R[x]$ so $p(x)$ is a zero-divisor.  $p$ is not a unit because if it was, then there would exist a $q(x)\neq 0$ so that $bp(x)q(x) = b = 0$, but $b\neq 0$.

-----
$\implies$

Let
$$
p_k = \sum_{j=0}^k a_j x^j.
$$
and we have $p_n=p$.

Suppose $p_k$ is a zero divisor in $R[x]$.  Then there exists a $g\in R[x]$
$$
g(x)=b_mx^m+b_{m-1}x^{m-1}+\cdots+b_0
$$
of least degree so that $g(x)p(x) = 0$.

Writing
$$
g(x)p(x) = \sum_{i=0}^{m+n} (gp)_i x^i,
$$

We have
$$
(gp)_{m+n} = \sum_{k=0}^{m+n} b_k a_{m+n-k} = 0.
$$

If $k>m$, then \(b_k=0\). If $k<m$, then $m+n-k>n$, so $a_{m+n-k}=0$.  So only one term survives,
$$
(gp)_{m+n} = b_m a_n = 0.
$$

So then $a_n g=0$ or has degree less than $m$.  By minimality of $g$, it must be zero.  Because $a_n g=0$, we have that 
$$
g(x)(a_{n-1}x^{n-1}+\cdots+a_1x+a_0)=0.
$$
With a similar argument to the above polynomial and applying induction we get that $b_m a_j=0$ for all $0 \le j \le n$.  But then this means $b_mp(x) = 0$.
