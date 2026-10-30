**Definitions and results used:** @[Frattini subgroup and nongenerators]cu:algebra:midterm-3:advanced:df:mt3-frattini-subgroup; @[Maximal subgroup]cu:algebra:midterm-3:foundations:df:mt3-maximal-subgroup; @[Generated subgroup and minimal generating set]cu:algebra:midterm-3:foundations:df:mt3-generated-subgroup; @[Zorn's lemma]math:set:axiom-choice:th:zorn-choice.

**Technique:** Outside Φ, a maximal subgroup witnesses generation; inside Φ, maximality forbids generation.

If $x\notin\Phi(G)$, some maximal subgroup $M$ excludes $x$. Maximality gives $\langle M,x\rangle=G$, so $x$ is not a nongenerator.

Conversely, suppose $x\in\Phi(G)$ and $\langle H,x\rangle=G$ for some $H<G$. There is a maximal proper subgroup containing $H$ in this particular situation: order the proper subgroups containing $H$ by inclusion. The union of a chain is still proper, because if it were $G$, one chain member would contain $x$, hence would contain $\langle H,x\rangle=G$. Zorn's lemma therefore supplies a maximal member $M$, which is maximal proper in $G$. But $x\in\Phi(G)\le M$ and $H\le M$ imply $G=\langle H,x\rangle\le M$, a contradiction.

For finite $G$, simply choose a maximal subgroup above $H$; Zorn's lemma is unnecessary. The chain argument is needed to cover the textbook's arbitrary-group statement.
