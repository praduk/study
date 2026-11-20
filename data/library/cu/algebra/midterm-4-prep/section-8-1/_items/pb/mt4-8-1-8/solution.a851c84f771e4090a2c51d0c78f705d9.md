**Strategy.** For (a), approximate each quotient by a quadratic integer with error strictly less than $1$. For (b), use a necessary condition for *any* Euclidean norm and show that the ring fails it.

**(a) Turn the remainder bound into a distance bound.** Set $d=|D|$. In the complex plane the @[field norm]mt4-quadratic-integers-norm is $N(z)=|z|^2$. Given $\alpha,\beta\in\mathcal O$ with $\beta\ne0$, put $z=\alpha/\beta$. If $q\in\mathcal O$ satisfies $|z-q|^2<1$, put $r=\alpha-q\beta$. By @[multiplicativity]mt4-quadratic-norm-units, the remainder satisfies the @[Euclidean condition]mt4-euclidean-domain because

$$
N(r)=N(\beta)|z-q|^2<N(\beta).
$$

- **For $d=1,2$**, the lattice basis is $1,i\sqrt d$. Round each coefficient of $z$ in this basis to a nearest integer. The horizontal error is at most $1/2$ and the vertical error at most $\sqrt d/2$, so $|z-q|^2\le(1+d)/4<1$.
- **For $d=3,7,11$**, the basis is $1,\omega$ with $\omega=(1+i\sqrt d)/2$. Adjacent horizontal lattice rows are $\sqrt d/2$ apart. Pick a nearest row, then a nearest lattice point on that row, where the horizontal spacing is $1$. The vertical error is at most $\sqrt d/4$ and the horizontal error at most $1/2$, so $|z-q|^2\le(4+d)/16\le15/16<1$.

This produces the required quotient for all five values of $D$.

**(b) Find the possible universal side divisors.** For $d=43,67,163$ use the same basis $1,\omega$. An element $a+b\omega$ with $a,b\in\Z$ and $b\ne0$ has norm

$$
(a+b/2)^2+db^2/4\ge d/4>9.
$$

Thus every element of norm at most $9$ is an ordinary integer. By the @[unit criterion]mt4-quadratic-norm-units, the only units are $1$ and $-1$.

If $u$ is a @[universal side divisor]mt4-universal-side-divisor, every $x$ has the form $x=qu+z$ with $z\in\{0,1,-1\}$. Take $x=2$. Then $u$ divides $1$, $2$, or $3$. A side divisor is a nonunit, so only $2$ and $3$ are possible dividends. In a factorization of either, the factors have positive integer norms with product $4$ or $9$. Both factors therefore have norm at most $9$ and are ordinary integers. This leaves $u=\pm2$ or $\pm3$.

**Rule out those four candidates.** Take $x=\omega$. Now $u$ would have to divide one of $\omega,\omega-1,\omega+1$. Each has $\omega$-coefficient $1$, whereas every multiple of $u$ in $\mathcal O$ has $\omega$-coefficient divisible by $2$ or $3$. This is impossible. Since $2$ is a nonzero nonunit, $\mathcal O$ is not a field. The @[universal side divisor criterion]mt4-euclidean-side-divisor now rules out every Euclidean norm.
