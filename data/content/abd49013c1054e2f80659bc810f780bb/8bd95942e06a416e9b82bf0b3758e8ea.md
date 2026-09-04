A set $\Gamma$ of formulas is **syntactically consistent** when

$$\Gamma\nvdash\false.$$

Equivalently, there is no formula $A$ such that both $\Gamma\vdash A$ and $\Gamma\vdash\neg A$. Indeed, such a pair yields $\false$ by $\neg E$; conversely, $\false E$ turns a derivation of $\false$ into derivations of both $A$ and $\neg A$. Consistency here is relative to the exact calculus declared in @math:prop:deduction:df:natural-deduction-calculus.
