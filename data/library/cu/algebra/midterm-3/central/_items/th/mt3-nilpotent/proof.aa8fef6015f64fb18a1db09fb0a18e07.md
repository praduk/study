**Definitions and results used:** @mt3-nilpotent-definition, @mt3-upper-central, @mt3-pgroup-nilpotent, @mt3-sylow-normality, @mt3-frattini-argument.

**1⇒2.** For $H<G$, choose the least $i$ with $Z_i(G)\nleq H$. If $z\in Z_i(G)\setminus H$, then the commutators of both $z$ and $z^{-1}$ with $H$ lie in $Z_{i-1}(G)\le H$. Thus $zHz^{-1}=H$, so $z\in N_G(H)\setminus H$.

**2⇒3.** Put $N=N_G(P)$ for a Sylow subgroup $P$. It is the unique Sylow $p$-subgroup of $N$, hence characteristic in $N$. Therefore every element normalizing $N$ normalizes $P$, giving $N_G(N)=N$. Criterion 2 forces $N=G$.

**3⇒4.** Normal Sylow subgroups of different prime orders commute: their commutators lie in their trivial intersection. The product of all factors has order $|G|$, and successive intersections are trivial by coprimality, giving the direct product.

**4⇒1.** Each Sylow factor is nilpotent. Centers and successive upper centers of a finite direct product are the products of the corresponding centers, so the product is nilpotent.

**2⇒5.** Maximality and strict normalizer growth give $N_G(M)=G$ for each maximal $M$.

**5⇒3.** If $N_G(P)<G$, put it inside a maximal subgroup $M$. By hypothesis $M\trianglelefteq G$, and $P$ is Sylow in $M$. Frattini gives $G=M N_G(P)=M$, contradiction.
