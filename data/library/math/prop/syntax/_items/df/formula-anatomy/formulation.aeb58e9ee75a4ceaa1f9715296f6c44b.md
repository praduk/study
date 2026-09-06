A **compound formula** is a formula produced by a unary or binary connective constructor. Its **main connective** is the connective at the root of its parse tree. Atoms and the logical constants $\true,\false$ have no main connective.

The **immediate subformulas** of $\neg A$ consist of $A$; those of $(A\circ B)$ consist of $A$ and $B$. Atoms and logical constants have no immediate subformulas.

A **subformula occurrence** is any node of the parse tree, including the root. A formula $B$ is a **subformula** of $A$ if some occurrence in the parse tree of $A$ is labeled by $B$. Repeated occurrences count separately as occurrences but only once when taking the set of distinct subformulas.
