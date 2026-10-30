**Definitions and results used:** @[Conjugation homomorphism, its centralizer kernel, and Lagrange theorem]mt3-foundations; @[Sylow divisibility and congruence in a quotient]mt3-sylow; @[Normal subgroups with trivial intersection commute]mt3-foundations; @[Coprime cyclic direct products are cyclic]mt3-abelian; @[A cyclic quotient by the center forces abelianity]mt3-pgroups.

**Technique:** A normal cyclic subgroup becomes central when the conjugation image has coprime possible orders; then use a cyclic central quotient.

Let $P\nsubg G$ have order $3$. Conjugation gives $G\to\Aut(P)\cong C_2$. Its image has order dividing both $105$ and $2$, hence is trivial; therefore $P\le Z(G)$.

The quotient $G/P$ has order $35$. Its Sylow counts satisfy $n_7\mid5$, $n_7\equiv1\pmod7$, and $n_5\mid7$, $n_5\equiv1\pmod5$, so both are $1$. Two normal subgroups of coprime orders commute: their commutators lie in their trivial intersection. Thus $G/P\cong C_7\times C_5\cong C_{35}$.

Choose $gP$ generating $G/P$. Every element of $G$ is $g^i z$ with $z\in P\le Z(G)$, so any two elements commute. Hence $G$ is abelian.
