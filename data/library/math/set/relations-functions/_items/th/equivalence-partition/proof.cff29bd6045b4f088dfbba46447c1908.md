Let $E$ be an equivalence relation. Reflexivity shows $a\in[a]_E$, so each class is nonempty and the classes cover $A$. If $[a]_E\cap[b]_E$ contains $x$, then $xEa$ and $xEb$. Symmetry and transitivity give $aEb$. For any $y$, $yEa$ then holds exactly when $yEb$, so $[a]_E=[b]_E$. Hence two classes are equal or disjoint, and the classes form a partition.

Conversely, let $\Pi$ partition $A$, and define $xEy$ when some block $C\in\Pi$ contains both $x$ and $y$. Every $x$ lies in a block, so $E$ is reflexive. The definition is symmetric. If $x,y\in C$ and $y,z\in D$, then $y\in C\cap D$, so the partition property gives $C=D$; hence $x,z$ lie in one block and $E$ is transitive.

Starting with $E$, its classes are the blocks just constructed. Starting with $\Pi$, the equivalence class of $a$ is the unique block containing $a$. Thus the constructions are inverse.
