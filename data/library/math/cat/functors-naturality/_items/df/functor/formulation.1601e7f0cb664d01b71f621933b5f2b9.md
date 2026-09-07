A functor $F:\mathcal C\to\mathcal D$ assigns objects and morphisms with $F(f):F(A)\to F(B)$ for $f:A\to B$, preserving identities and composition: $F(\id_A)=\id_{F(A)}$, $F(gf)=F(g)F(f)$.

A contravariant functor from $\mathcal C$ to $\mathcal D$ means an ordinary functor $\mathcal C^{\mathrm{op}}\to\mathcal D$. It reverses the direction of each arrow. For example $V\mapsto V^*=\Hom_k(V,k)$ is contravariant, sending $f:V\to W$ to $f^*:W^*\to V^*$ by precomposition. Forgetting group structure gives a covariant functor $\Grp\to\Set$.
