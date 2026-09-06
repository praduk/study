Recursion defines natural-number arithmetic. For each $m\in\omega$, addition is the unique function of $n$ satisfying

$$
m+0=m,
\qquad
m+S(n)=S(m+n).
$$

Multiplication is then defined by

$$
m\cdot0=0,
\qquad
m\cdot S(n)=m\cdot n+m.
$$

Exponentiation is defined by $m^0=1$ and $m^{S(n)}=m^n\cdot m$. Induction proves closure in $\omega$, associativity and commutativity of addition and multiplication, distributivity, and the familiar order laws. These laws are theorems about the recursively defined operations, not part of their definitions.
