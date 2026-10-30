**Definitions and results used:** @[finite abelian decomposition and characters of cyclic groups]mt3-abelian; @[homomorphisms and direct products]mt3-foundations.

**Technique:** Choose cyclic factors; define one coordinate character per factor and evaluate at generators to prove independence.

**(a)** For characters $\chi,\psi$, define $(\chi\psi)(g)=\chi(g)\psi(g)$. Because the target is abelian,

$$
(\chi\psi)(gh)=\chi(g)\chi(h)\psi(g)\psi(h)=(\chi\psi)(g)(\chi\psi)(h).
$$

Thus the product is a character. Associativity and commutativity are pointwise; the identity is the constant character $1$ and the inverse is $\chi^{-1}(g)=\chi(g)^{-1}$.

**(b)** Write $G=\langle x_1\rangle\times\cdots\times\langle x_r\rangle$ with $|x_i|=n_i$. Define $\chi_i(x_i)=e^{2\pi i/n_i}$ and $\chi_i(x_j)=1$ for $j\ne i$, extending multiplicatively. Then $|\chi_i|=n_i$. For any character $\chi$, the relation $x_i^{n_i}=1$ forces $\chi(x_i)$ to be an $n_i$th root of unity, say $e^{2\pi i a_i/n_i}$. Hence

$$
\chi=\prod_i\chi_i^{a_i}.
$$

If this product is the trivial character, evaluating at each $x_i$ gives $n_i\mid a_i$. Therefore

$$
\widehat G=\langle\chi_1\rangle\times\cdots\times\langle\chi_r\rangle\cong G.
$$

The isomorphism depends on choices of cyclic generators and roots; it is noncanonical.
