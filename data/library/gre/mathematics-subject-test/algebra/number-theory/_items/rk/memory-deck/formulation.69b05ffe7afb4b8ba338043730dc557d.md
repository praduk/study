## Divisibility and the Euclidean algorithm

$a\mid b$ means $b=ak$ for some integer $k$. The greatest common divisor is a linear combination:

$$
\gcd(a,b)=ax+by.
$$

Thus $ax+by=c$ has integer solutions iff $\gcd(a,b)\mid c$. If $d=\gcd(a,b)$ and $(x_0,y_0)$ is one solution, all solutions are

$$
x=x_0+\frac bd t,\qquad y=y_0-\frac ad t,\qquad t\in\mathbb Z.
$$

## Congruences

$a\equiv b\pmod n$ iff $n\mid a-b$. The class of $a$ is invertible modulo $n$ iff $\gcd(a,n)=1$. The congruence $ax\equiv b\pmod n$ has solutions iff $\gcd(a,n)\mid b$; when it does, there are $\gcd(a,n)$ incongruent solutions modulo $n$.

## Exponent reduction

If $p\nmid a$ and $p$ is prime,

$$
a^{p-1}\equiv1\pmod p.
$$

If $\gcd(a,n)=1$,

$$
a^{\varphi(n)}\equiv1\pmod n.
$$

For $n=\prod p_i^{e_i}$,

$$
\varphi(n)=n\prod_{p\mid n}\left(1-\frac1p\right).
$$

Check coprimality before reducing an exponent. A shorter observed cycle can beat Euler's exponent.

## Chinese remainder theorem

For pairwise coprime moduli $n_i$, a system $x\equiv a_i\pmod{n_i}$ has one solution modulo $\prod n_i$. For non-coprime moduli, solutions exist only when residues agree modulo every pairwise gcd.

## Prime factorization arithmetic

If $n=\prod p_i^{e_i}$, then

$$
\tau(n)=\prod(e_i+1),
$$

$$
\sigma(n)=\prod_i\frac{p_i^{e_i+1}-1}{p_i-1}.
$$

The exponent of a prime $p$ in $n!$ is

$$
v_p(n!)=\sum_{k\ge1}\left\lfloor\frac n{p^k}\right\rfloor.
$$

## Fast recognition

Use gcd for linear congruences, factor the modulus before using $\varphi$, combine $-1$ residues immediately, and exploit parity or residues modulo small integers before attempting a long Diophantine search.
