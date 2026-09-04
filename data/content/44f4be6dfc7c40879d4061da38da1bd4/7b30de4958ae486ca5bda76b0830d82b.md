The set $\mathsf{Form}$ of **formulas** is the least set satisfying these clauses:

- Every $p\in\mathsf{Prop}$ is a formula.
- $\true$ and $\false$ are formulas.
- If $A$ is a formula, then $\neg A$ is a formula.
- If $A$ and $B$ are formulas and $\circ\in\{\land,\lor,\to,\leftrightarrow\}$, then $(A\circ B)$ is a formula.

Nothing else is a formula. Formulas are treated as finite tagged trees, so constructors are disjoint and retain their immediate children. In ordinary display, outer parentheses may be omitted and the precedence convention $\neg$ before $\land$ before $\lor$ before $\to$ before $\leftrightarrow$ may be used. Associativity is never part of the syntax: an omitted grouping must still be recoverable from an announced convention.
