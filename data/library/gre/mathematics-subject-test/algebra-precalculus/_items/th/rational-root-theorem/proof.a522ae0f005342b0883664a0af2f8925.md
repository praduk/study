$\gcd(p,q)=1 \implies p\nmid q \text{ and } q\nmid p$.

Plug in $p/q$ into the polynomial to get
$$
a_n \left(\frac{p}{q} \right)^n + a_n \left(\frac{p}{q} \right)^{n-1} + \cdots a_0 = 0
$$
Clearing denominators
$$
a_n p^n + a_n p^{n-1} q + \cdots + pq^{n-1} a_0 + q^n a_0 = 0.
$$

Moving $a_0$ term to the other side, $p \mid a_0$ because $p\nmid q$.

Moving $a_n$ term to the other side, $q \mid a_n$ because $q\nmid p$.
