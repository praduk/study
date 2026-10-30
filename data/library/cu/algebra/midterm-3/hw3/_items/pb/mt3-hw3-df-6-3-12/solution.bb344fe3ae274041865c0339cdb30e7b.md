**Definitions and results used:** @[Free group on a set]cu:algebra:midterm-3:advanced:df:mt3-free; @[Universal mapping property of free and presented groups]cu:algebra:midterm-3:advanced:th:mt3-free-maps; @[Lower central series]cu:algebra:midterm-3:foundations:df:mt3-lower-central; @[Characteristic terms and functoriality of the three series]cu:algebra:midterm-3:foundations:th:mt3-series-functorial; @[Equivalence of the upper and lower nilpotence criteria]cu:algebra:midterm-3:central:th:mt3-central-series-equivalence; @[Factoring a homomorphism through a quotient]cu:algebra:midterm-3:foundations:th:mt3-factor-quotient.

**Technique:** Start with a free group, quotient by exactly the relations needed, and prove every target map kills those relations.

Let $F=F(S)$ be the free group on $S$. Use the indexing $\gamma_1(F)=F$ and $\gamma_{i+1}(F)=[F,\gamma_i(F)]$, and define

$$
N_c(S)=F/\gamma_{c+1}(F).
$$

Let $\iota:S\to N_c(S)$ be the canonical map. The lower central series commutes with a surjective homomorphism, so $\gamma_{c+1}(N_c(S))=1$; hence the quotient is nilpotent of class at most $c$.

Given any nilpotent group $H$ of class at most $c$ and any set map $f:S\to H$, freeness gives a unique homomorphism $\widetilde f:F\to H$ extending $f$. Homomorphisms preserve commutators, so

$$
\widetilde f(\gamma_{c+1}(F))\le\gamma_{c+1}(H)=1.
$$

Thus $\widetilde f$ factors uniquely through the quotient to a homomorphism $\overline f:N_c(S)\to H$ with $\overline f\circ\iota=f$. Uniqueness also follows because $\iota(S)$ generates the quotient. This is the required universal property.

Any other group with this property has unique maps to and from $N_c(S)$ fixing the specified generators; the composites fix the generators and therefore are identity maps. Thus the object is unique up to a unique generator-preserving isomorphism.

**Convention check:** “class $c$” here means the free object among groups of class **at most** $c$. Exact class $c$ is not possible for every set $S$: the empty set gives the trivial group, and a singleton gives $\Z$, of class $1$, even when $c>1$. With the lecture's indexing $G_{(0)}=G$, the denominator is $F_{(c)}$.
