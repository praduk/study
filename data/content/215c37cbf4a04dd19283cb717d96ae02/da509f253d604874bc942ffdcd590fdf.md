For a set $\Gamma$ of formulas,

$$\Gamma\vdash A$$

means that there is a finite natural-deduction derivation ending in $A$ whose undischarged assumptions are all members of $\Gamma$. Only finitely many members of $\Gamma$ can occur in any such derivation.

For a finite displayed premise list,

$$A_1,\ldots,A_n\vdash B$$

is shorthand for $\{A_1,\ldots,A_n\}\vdash B$; in particular, $A\vdash B$ uses the singleton premise set $\{A\}$. If $n=0$, write $\vdash B$ and call $B$ a **theorem** of the calculus.

Formulas $A$ and $B$ are **proof-theoretically equivalent** when $A\vdash B$ and $B\vdash A$. This is a syntactic notion. Its agreement with logical equivalence requires soundness and completeness; it is not true merely by notation.
