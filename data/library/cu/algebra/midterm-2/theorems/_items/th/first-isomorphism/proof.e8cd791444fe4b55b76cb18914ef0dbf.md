**Kernel and image.** If $x\in K$ and $g\in G$, then $f(gxg^{-1})=f(g)1f(g)^{-1}=1$, so conjugation preserves $K$ and $K\nsubg G$. The subgroup tests for kernel and image follow from $f(ab^{-1})=f(a)f(b)^{-1}$.

**Well-definedness and injectivity together.** For $g,h\in G$,

$$
gK=hK\iff h^{-1}g\in K\iff f(h)^{-1}f(g)=1\iff f(g)=f(h).
$$

Thus the proposed map does not depend on the coset representative, and two cosets have the same image only if they are equal.

**Homomorphism and surjectivity.** The coset product gives $\bar f((gK)(hK))=f(gh)=f(g)f(h)=\bar f(gK)\bar f(hK)$. Every element of $f(G)$ is some $f(g)$, so the map is onto. Together with injectivity this proves the isomorphism.

**Working rule:** to understand a quotient, first construct a map from the original group whose kernel is the proposed denominator.
