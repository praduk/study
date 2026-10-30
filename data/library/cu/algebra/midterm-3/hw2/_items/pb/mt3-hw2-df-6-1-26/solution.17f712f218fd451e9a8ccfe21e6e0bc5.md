**Definitions and results used:** @[Frattini subgroup and nongenerators]cu:algebra:midterm-3:advanced:df:mt3-frattini-subgroup; @[Maximal subgroups of a finite p-group]cu:algebra:midterm-3:sylow:th:mt3-pgroup-maximal; @[Maximal subgroup]cu:algebra:midterm-3:foundations:df:mt3-maximal-subgroup; @[Elementary abelian p-group]cu:algebra:midterm-3:foundations:df:mt3-elementary-abelian; @[Vector spaces, bases, and linear maps over F_p]cu:algebra:midterm-3:foundations:df:mt3-linear; @[Counting lines and hyperplanes over F_p]cu:algebra:midterm-3:foundations:th:mt3-lines-hyperplanes; @[Automorphisms and order of an elementary abelian group]cu:algebra:midterm-3:foundations:th:mt3-linear-automorphisms; @[Fixed-point congruence for p-group actions]cu:algebra:midterm-3:foundations:th:mt3-fixed-points; @[Subgroup correspondence for a quotient]cu:algebra:midterm-3:foundations:th:mt3-quotient-correspondence; @[Factoring a homomorphism through a quotient]cu:algebra:midterm-3:foundations:th:mt3-factor-quotient; @[Generated subgroup and minimal generating set]cu:algebra:midterm-3:foundations:df:mt3-generated-subgroup.

**Technique:** Maximal p-group subgroups give linearization; lift a basis; use coprime orbit counting to lift fixed basis vectors.

**(a) Elementary abelian quotient.** Every maximal subgroup $M$ of a finite $p$-group is normal of index $p$. Thus $P/M\cong C_p$, so $P'\le M$ and $x^p\in M$ for every $x\in P$. Intersecting all $M$ gives $P'\le\Phi(P)$ and $x^p\in\Phi(P)$. Therefore $P/\Phi(P)$ is abelian of exponent dividing $p$, hence a vector space over $\F_p$.

**(b) Universal property.** Suppose $P/N=V$ is elementary abelian. Every nonzero vector of $V$ is excluded by some hyperplane. The inverse images of these hyperplanes are maximal subgroups of $P$, and their intersection is $N$. Hence $\Phi(P)\le N$ (also immediate when $N=P$).

Consequently every homomorphism $f:P\to E$ to an elementary abelian $p$-group factors uniquely through $\pi:P\to P/\Phi(P)$: its image is elementary abelian, so $\Phi(P)\le\ker f$, and $\overline f(x\Phi(P))=f(x)$. The diagram commutes, meaning $f=\overline f\circ\pi$:

$$
\begin{array}{ccc}
P&\xrightarrow{f}&E\\
\pi\downarrow&&\uparrow\overline f\\
P/\Phi(P)&\xrightarrow{\mathrm{id}}&P/\Phi(P).
\end{array}
$$

Equivalently, with $P^p=\langle x^p:x\in P\rangle$, part (a) gives $P'P^p\le\Phi(P)$ and applying (b) to $P'P^p$ gives $\boxed{\Phi(P)=P'P^p}$.

**(c) Basis lifts and minimal generators.** If $H\le P$ and $H\Phi(P)=P$, then $H=P$: otherwise a maximal subgroup $M$ containing $H$ also contains $\Phi(P)$, contradicting $H\Phi(P)=P$. Thus lifts $x_1,\ldots,x_r$ of a basis generate $P$. Conversely, images of any $s$ generators span the $r$-dimensional space, so $s\ge r$. A generating set with dependent images has one redundant image; deleting its corresponding generator still gives a spanning set, whose lifts still generate by the same argument. Hence an inclusion-minimal generating set has basis images. Conversely, basis images ensure that removing any generator fails to span, so the lifts are minimal. Every minimal generating set therefore has exactly $r$ elements.

**(d) Cyclicity.** A cyclic elementary abelian quotient has dimension at most $1$, so (c) gives at most one generator of $P$. Since $P'\le\Phi(P)$, the quotient $P/\Phi(P)$ is a quotient of $P/P'$; if the latter is cyclic, so are the former and $P$.

**(e) Fixed point in a fixed coset.** The coset is $\alpha$-invariant because $\Phi(P)$ is characteristic. Its cardinality is $|\Phi(P)|=p^a$. The orbits under $\langle\alpha\rangle$ have size $1$ or $q$. Since $q\nmid p^a$, at least one orbit has size $1$.

**(f) Faithfulness of coprime action.** First let $\beta$ have prime order $q\ne p$ and act trivially on $\overline P$. By (e), choose a $\beta$-fixed lift of each basis vector. These lifts generate by (c), so $\beta$ fixes all of $P$, a contradiction. If a nonidentity $\alpha$ of coprime order $m$ acted trivially, then for any prime $q\mid m$, the automorphism $\alpha^{m/q}$ would have prime order $q\ne p$ and act trivially, also impossible. Finally the homomorphism $\Aut(P)\to\Aut(\overline P)=\GL_r(\F_p)$ has trivial kernel on every subgroup of order prime to $p$, proving the embedding.
