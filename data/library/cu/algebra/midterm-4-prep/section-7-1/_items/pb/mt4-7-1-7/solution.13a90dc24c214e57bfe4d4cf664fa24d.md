**Strategy.** Use the @[subring test]mt4-subring to show that the center is a subring, then check that it contains $1$. Centrality gives commutativity. To prove the center of a division ring is a field, we still need to show that inverses of nonzero central elements lie in the center.

**1. Verify the subring test.** By the @[definition of the center]mt4-ring-center, an element belongs to $Z(R)$ exactly when it commutes with every $r\in R$.

- **Nonempty.** For every $r\in R$, @[multiplication by zero]mt4-ring-arithmetic gives $0r=r0=0$. Thus $0\in Z(R)$.
- **Subtraction.** Take $z,w\in Z(R)$ and any $r\in R$. By the @[ring laws]mt4-ring and centrality, $(z-w)r=zr-wr=rz-rw=r(z-w)$.
- **Multiplication.** First move $r$ past $w$ to get $(zw)r=z(rw)$. Then move it past $z$ to get $z(rw)=(rz)w=r(zw)$.

**2. Check the identity and commutativity.** For every $r\in R$, $1r=r=r1$, so $1\in Z(R)$. If $z,w\in Z(R)$, then $z$ commutes with every element of $R$, including $w$. Thus $zw=wz$.

**3. Show that inverses stay in the center.** Now suppose $R$ is a @[division ring]mt4-division-ring and take $0\ne z\in Z(R)$. Its inverse $z^{-1}$ exists in $R$. Fix $r\in R$. Multiplying $zr=rz$ on the left by $z^{-1}$ gives $r=z^{-1}rz$. Multiplying this equality on the right by $z^{-1}$ gives

$$
rz^{-1}=z^{-1}r.
$$

Thus $z^{-1}$ commutes with every $r$, so $z^{-1}\in Z(R)$. The center is a commutative ring with $1\ne0$ and inverses for all its nonzero elements. Hence it is a @[field]mt4-field.
