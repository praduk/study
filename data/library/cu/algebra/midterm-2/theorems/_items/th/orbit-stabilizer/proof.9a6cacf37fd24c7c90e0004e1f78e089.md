First $G_a$ is a subgroup: the identity fixes $a$, and if $g,h$ fix $a$, then $h^{-1}$ fixes $a$ and $(gh^{-1})\cdot a=g\cdot a=a$.

For $g,h\in G$,

$$
g\cdot a=h\cdot a\iff (h^{-1}g)\cdot a=a\iff h^{-1}g\in G_a\iff gG_a=hG_a.
$$

This equivalence proves both well-definedness and injectivity of the displayed coset map. Surjectivity holds because every point in the orbit is by definition some $g\cdot a$. Thus it is a bijection, proving the orbit-size formula.

Each $g$ acts by a bijection of $A$, with inverse the action of $g^{-1}$. The action law shows $\rho(gh)=\rho(g)\rho(h)$, so $\rho:G\to S_A$ is a homomorphism. Its kernel consists of the elements acting as the identity permutation, exactly those fixing every $a\in A$. This is $\bigcap_aG_a$.
