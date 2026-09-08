Let $\phi_a(z)=(z-a)/(1-\overline a z)$. Algebra gives

$$
1-|\phi_a(z)|^2=\frac{(1-|a|^2)(1-|z|^2)}{|1-\overline a z|^2}>0
$$

on the disk, and its inverse is $(w+a)/(1+\overline a w)$, which also maps the disk into itself. Thus $\phi_a$ is a biholomorphism taking $a$ to zero. For any disk automorphism $f$, let $a=f^{-1}(0)$ and $g=f\circ\phi_a^{-1}$. @[Schwarz's lemma]math:complex:conformal-maps:th:schwarz applied to $g$ and $g^{-1}$ gives $|g(z)|\le|z|\le|g(z)|$. Its equality case forces $g(z)=e^{i\theta}z$. Composition gives the formula. Conversely, $\phi_a$ and the rotation are biholomorphisms, so every displayed map is one.
