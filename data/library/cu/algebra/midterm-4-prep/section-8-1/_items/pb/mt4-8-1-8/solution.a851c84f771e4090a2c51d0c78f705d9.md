**Strategy.** For (a), approximate each quotient by a quadratic integer with error strictly less than $1$. For (b), use a necessary condition for *any* Euclidean norm and show that the ring fails it.

**(a) Turn the remainder bound into a distance bound.** Set $d=|D|$. In the complex plane the @[field norm]mt4-quadratic-integers-norm is $N(z)=|z|^2$. Given $\alpha,\beta\in\mathcal O$ with $\beta\ne0$, put $z=\alpha/\beta$. If $q\in\mathcal O$ satisfies $|z-q|^2<1$, put $r=\alpha-q\beta$. By @[multiplicativity]mt4-quadratic-norm-units, the remainder satisfies the @[Euclidean condition]mt4-euclidean-domain because

$$
N(r)=N(\beta)|z-q|^2<N(\beta).
$$

- **For $d=1,2$**, the lattice basis is $1,i\sqrt d$. Round each coefficient of $z$ in this basis to a nearest integer. The horizontal error is at most $1/2$ and the vertical error at most $\sqrt d/2$, so $|z-q|^2\le(1+d)/4<1$.
- **For $d=3,7,11$**, the basis is $1,\omega$ with $\omega=(1+i\sqrt d)/2$. Each lattice parallelogram splits along the diagonal joining $1$ to $\omega$ (or its translate) into two congruent triangles. Thus $z$ lies in a triangle congruent to the one with vertices $0,1,\omega$.

**Get the bound in the hint.** The circumcenter of the triangle $0,1,\omega$ is on the perpendicular bisector of $[0,1]$, so write it as $1/2+it$. Equating its squared distances to $0$ and $\omega$ gives $1/4+t^2=(\sqrt d/2-t)^2$. Hence $t=(d-1)/(4\sqrt d)$ and the squared circumradius is
$$
\rho^2=\tfrac14+t^2=\frac{(1+d)^2}{16d}.
$$

To see why this radius suffices, let $v_1,v_2,v_3$ be the vertices of the triangle containing $z$ and let $c$ be its circumcenter. Since $z$ is in the triangle, write $z=\sum_j\lambda_jv_j$ with $\lambda_j\ge0$ and $\sum_j\lambda_j=1$. Expanding the squares and using $|v_j-c|=\rho$ gives
$$
\sum_j\lambda_j |z-v_j|^2=\rho^2-|z-c|^2\le\rho^2.
$$
At least one vertex $q$ therefore has $|z-q|^2\le\rho^2$. For $d=3,7,11$ the bound is respectively $1/3,4/7,9/11$, all less than $1$. This supplies the required quotient in the remaining three cases.

**(b) Find the possible universal side divisors.** For $d=43,67,163$ use the same basis $1,\omega$. An element $a+b\omega$ with $a,b\in\Z$ and $b\ne0$ has norm

$$
(a+b/2)^2+db^2/4\ge d/4>9.
$$

Thus every element of norm at most $9$ is an ordinary integer. By the @[unit criterion]mt4-quadratic-norm-units, the only units are $1$ and $-1$.

If $u$ is a @[universal side divisor]mt4-universal-side-divisor, every $x$ has the form $x=qu+z$ with $z\in\{0,1,-1\}$. Take $x=2$. Then $u$ divides $1$, $2$, or $3$. A side divisor is a nonunit, so only $2$ and $3$ are possible dividends. In a factorization of either, the factors have positive integer norms with product $4$ or $9$. Both factors therefore have norm at most $9$ and are ordinary integers. This leaves $u=\pm2$ or $\pm3$.

**Rule out those four candidates.** Take $x=\omega$. Now $u$ would have to divide one of $\omega,\omega-1,\omega+1$. Each has $\omega$-coefficient $1$, whereas every multiple of $u$ in $\mathcal O$ has $\omega$-coefficient divisible by $2$ or $3$. This is impossible. Since $2$ is a nonzero nonunit, $\mathcal O$ is not a field. The @[universal side divisor criterion]mt4-euclidean-side-divisor now rules out every Euclidean norm.
