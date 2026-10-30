**Definition used:** @mt3-frattini-subgroup. The arbitrary-group proof uses Zorn's lemma: a partially ordered set in which every chain has an upper bound has a maximal element.

Automorphisms permute maximal subgroups, so preserve their intersection, including the no-maximal-subgroup convention. If $x\notin\Phi(G)$, some maximal $M$ excludes $x$, and $\langle M,x\rangle=G$; hence $x$ is not a nongenerator.

Conversely suppose $x\in\Phi(G)$ and $\langle H,x\rangle=G$ for some proper $H$. Consider the proper subgroups containing $H$, ordered by inclusion. A chain's union is still proper: if it were $G$, some member would contain $x$ and therefore all of $\langle H,x\rangle=G$, contradiction. Zorn supplies a maximal proper subgroup $M$ containing $H$. But $x\in\Phi(G)\le M$ contradicts generation of $G$.

For the final finite-group assertion, if $H<G$, choose a maximal subgroup $M$ containing $H$. It also contains $\Phi(G)$, so $H\Phi(G)\le M<G$.
