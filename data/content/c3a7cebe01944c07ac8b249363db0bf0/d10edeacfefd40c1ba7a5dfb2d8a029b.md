The **rank** $\operatorname{rk}(A)$ and the finite set $\operatorname{At}(A)$ of atoms occurring in $A$ are defined recursively. For an atom $p$ and $c\in\{\true,\false\}$,

$$\operatorname{rk}(p)=\operatorname{rk}(c)=0,\qquad \operatorname{At}(p)=\{p\},\qquad \operatorname{At}(c)=\varnothing.$$

For negation,

$$\operatorname{rk}(\neg A)=1+\operatorname{rk}(A),\qquad \operatorname{At}(\neg A)=\operatorname{At}(A).$$

For a binary connective $\circ$,

$$\operatorname{rk}(A\circ B)=1+\max\{\operatorname{rk}(A),\operatorname{rk}(B)\},$$

$$\operatorname{At}(A\circ B)=\operatorname{At}(A)\cup\operatorname{At}(B).$$

Rank is the height of the parse tree, not its number of connective occurrences.
