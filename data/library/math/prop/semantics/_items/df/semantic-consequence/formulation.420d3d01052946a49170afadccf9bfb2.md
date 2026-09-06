For a set $\Gamma$ of formulas and a formula $A$,

$$\Gamma\models A$$

means that every valuation satisfying $\Gamma$ also satisfies $A$. This is **semantic consequence**. An argument with premises $\Gamma$ and conclusion $A$ is semantically valid exactly when $\Gamma\models A$.

For a finite displayed premise list,

$$A_1,\ldots,A_n\models B$$

is shorthand for $\{A_1,\ldots,A_n\}\models B$; in particular, $A\models B$ uses the singleton premise set $\{A\}$. If $n=0$, the condition becomes validity of $B$, written $\models B$. If $\Gamma$ is unsatisfiable, then $\Gamma\models A$ for every formula $A$; this is vacuous consequence, not evidence that $A$ is itself valid.
