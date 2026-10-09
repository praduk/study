**Step 1: normality of the generated subgroup.** For $g,x,y\in G$, conjugation preserves products and inverses, so

$$
g[x,y]g^{-1}=[gxg^{-1},gyg^{-1}].
$$

The right side is again one of the generators defining $N$. Conjugation by $g$ therefore carries every word in those generators and their inverses into $N$. Thus $gNg^{-1}\subseteq N$. Applying the argument to $g^{-1}$ gives equality. This proves normality without assuming $N$ finite.

**Step 2: commutativity in the quotient.** Write $\bar x=xN$. Because $[x,y]\in N$,

$$
\bar x^{-1}\bar y^{-1}\bar x\bar y=N.
$$

Multiplying this equality on the left first by $\bar x$ and then by $\bar y$ gives $\bar x\bar y=\bar y\bar x$. Every quotient element is some $xN$, so the quotient is abelian.

**A useful stronger conclusion.** If $K\nsubg G$ and $G/K$ is abelian, the same quotient calculation shows $[x,y]\in K$ for every $x,y$. Therefore $N\le K$. Conversely $N\le K$ makes every commutator vanish in $G/K$. Thus

$$
G/K\text{ abelian}\quad\Longleftrightarrow\quad G'\le K,
$$

where $G'=N$. This criterion will be used in the solvability and perfect-group problems.

**Technique:** show that conjugation preserves a generating family, then turn a desired quotient identity into an element of the kernel.

**Foundations:** @cu:algebra:midterm-2:definitions:df:normal-quotient, @cu:algebra:midterm-2:theorems:th:commutator-criterion.
