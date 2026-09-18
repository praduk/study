Take the dyadic rationals

$$
H=\left\{\frac{m}{2^j}:m\in\Z,\ j\in\Z_{\ge0}\right\}.
$$

It contains $0$ and is closed under subtraction after passing to a common power-of-two denominator, so $H\le(\Q,+)$. It is proper because $1/3\notin H$: $1/3=m/2^j$ would imply $3m=2^j$.
If $H=\langle m/2^j\rangle$, the generator cannot be zero. But $1/2^{j+1}\in H$ would then be an integer multiple $t(m/2^j)$, yielding $1=2tm$, impossible. Thus $H$ is not cyclic.

**Technique:** construct a subgroup using restricted denominators; disprove generation by producing an element with a new denominator.
