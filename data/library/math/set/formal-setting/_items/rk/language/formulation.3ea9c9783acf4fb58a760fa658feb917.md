The object language of ZF is classical first-order logic with equality and one binary nonlogical relation symbol, $\in$. Every variable ranges over sets; there is no separate object-language sort for atoms, classes, or numbers.

Thus $x\in y$ is atomic, while $x\subseteq y$ is an abbreviation for

$$
\forall z\,(z\in x\to z\in y).
$$

Bounded quantifiers are also abbreviations:

$$
\forall x\in A\,\varphi \quad\text{means}\quad
\forall x(x\in A\to\varphi),
$$

and similarly $\exists x\in A\,\varphi$ means $\exists x(x\in A\land\varphi)$.

Keep object language and metatheory distinct. A displayed formula is an object-language expression. Statements about formulas, proofs, models, or all ordinals are normally made in the mathematical metatheory.
