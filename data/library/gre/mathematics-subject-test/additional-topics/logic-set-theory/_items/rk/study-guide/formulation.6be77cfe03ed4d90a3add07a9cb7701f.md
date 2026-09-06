## Core facts

In propositional logic, an implication $P\Rightarrow Q$ is false only when $P$ is true and $Q$ is false. It is equivalent to $\neg P\lor Q$ and to its contrapositive $\neg Q\Rightarrow\neg P$, but not to its converse. De Morgan's laws interchange conjunction and disjunction while negating every component.

Negating quantifiers also interchanges them:

$$
\neg(\forall x\,P(x))\equiv\exists x\,\neg P(x),\qquad
\neg(\exists x\,P(x))\equiv\forall x\,\neg P(x).
$$

Quantifier order matters: $\forall x\exists y$ generally differs from $\exists y\forall x$. A universal statement over an empty set is vacuously true, while an existential statement over an empty set is false.

For sets, translate $A\subseteq B$ as $\forall x(x\in A\Rightarrow x\in B)$. Know union, intersection, complement, difference, Cartesian product, power set, and symmetric difference. Set equality is normally proved by double inclusion or elementwise equivalence. De Morgan's laws apply to arbitrary indexed unions and intersections.

A relation may be reflexive, symmetric, antisymmetric, or transitive. Equivalence relations correspond to partitions. Partial orders are reflexive, antisymmetric, and transitive; a total order also compares every pair. For functions, keep injective, surjective, and bijective distinct. A left inverse implies injectivity, a right inverse implies surjectivity, and a two-sided inverse gives bijectivity.

The integers and finite strings over a finite alphabet are countable. Countable unions of countable sets are countable under the usual choice assumptions used in undergraduate mathematics. The real numbers and $\mathcal P(\mathbb N)$ are uncountable, and Cantor's theorem gives $|A|<|\mathcal P(A)|$ for every set $A$.

## Recognition cues

- Translate prose into quantifiers before negating or taking a converse.
- For subset identities, test membership of an arbitrary element.
- To refute a universal claim, seek one small counterexample, often involving $\varnothing$ or a singleton.
- For cardinality, look for an explicit enumeration, injection, surjection, or diagonal argument.

## Edge cases and traps

- Necessary and sufficient conditions point in opposite directions.
- $A\in B$ and $A\subseteq B$ are different statements.
- Pairwise disjoint events or sets need not be independent in a probabilistic sense.
- Antisymmetric does not mean “not symmetric.”
- The image of an intersection need not equal the intersection of the images unless injectivity supplies the missing implication.
