Let $(M,g)$ be an oriented pseudo-Riemannian $n$-manifold with @math:diffgeo:geometric-structures:df:pseudo-metric. In an oriented chart its metric volume form is

$$
\operatorname{vol}_g=\sqrt{|\det(g_{ij})|}\,dx^1\w\cdots\w dx^n.
$$

The Hodge star is the unique bundle map $\star_g:\Lambda^kT^*M\to\Lambda^{n-k}T^*M$ characterized by

$$
\alpha\w\star_g\beta=\langle\alpha,\beta\rangle_g\operatorname{vol}_g
$$

for all $k$-forms $\alpha,\beta$. The wedge pairing is nondegenerate in a basis of @math:diffgeo:forms:df:exterior-algebra, so this equation determines a unique @[smooth map]math:diffgeo:manifolds:df:smooth-map. Both metric and orientation are inputs; the @math:diffgeo:forms:df:exterior-derivative needs neither. Reversing orientation negates $\star_g$.

On oriented Euclidean three-space, $\star dx=dy\w dz$ and $\star(dx\w dy)=dz$. On Minkowski space with $x^0=ct$, metric $(-+++)$ and orientation $dx^0\w dx\w dy\w dz$, $\star(dx^0\w dx)=-dy\w dz$ and $\star(dy\w dz)=dx^0\w dx$. These signs fix the electromagnetic convention.
