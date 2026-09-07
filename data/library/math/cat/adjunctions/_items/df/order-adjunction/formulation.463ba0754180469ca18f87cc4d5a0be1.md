For posets $P,Q$ treated as categories, an adjunction $f\dashv g$ consists of monotone maps $f:P\to Q$ and $g:Q\to P$ such that

$$
f(p)\le q\quad\Longleftrightarrow\quad p\le g(q).
$$

Each Hom set is empty or a singleton, so this equivalence is exactly the adjunction's Hom bijection. The unit and counit become $p\le gf(p)$ and $fg(q)\le q$. The composite $gf$ is a closure operator: it is monotone, extensive, and idempotent. Indeed extensivity gives $gf(p)\le gfgf(p)$, and applying $g$ to $fgf(p)\le f(p)$ gives the reverse inequality.
