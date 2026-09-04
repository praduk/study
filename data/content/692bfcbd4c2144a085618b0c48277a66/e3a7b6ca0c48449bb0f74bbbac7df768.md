The map

$$
\pi(m,n)=\frac{(m+n)(m+n+1)}2+n
$$

is a bijection $\omega\times\omega\to\omega$: pairs are listed along successive diagonals $m+n=s$, and the triangular-number offset counts all earlier diagonals. The set $\omega^0$ consists of the empty function and is therefore a singleton. For each positive finite $k$, induction using the displayed pairing bijection gives a bijection between $\omega^k$ and $\omega$.

For the union, define $E:\omega\times\omega\to\bigcup_n A_n$ by $E(n,m)=e_n(m)$. It is surjective. Composing with the inverse of $\pi$ produces a surjection from $\omega$ onto the union. If the union is nonempty, map each element $x$ to the least index $r\in\omega$ at which that enumeration attains $x$; this is an injection into $\omega$. Hence the union is countable.

The supplied sequence $(e_n)$ matters. The assertion that every countable union of countable sets is countable, when the enumerations are not given, requires a weak choice principle and is not a theorem of bare ZF.
