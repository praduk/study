Define

$$
V=\{1,(1\ 2)(3\ 4),(1\ 3)(2\ 4),(1\ 4)(2\ 3)\}.
$$

The three nonidentity elements have order $2$, and the product of any two distinct ones is the third. Therefore $V$ is a subgroup isomorphic to $V_4$. Conjugation in $S_4$ relabels the points of a double transposition, so it preserves this set. Hence $V\nsubg A_4$.

Take $L=\langle(1\ 2)(3\ 4)\rangle$. The chain

$$
1\nsubg L\nsubg V\nsubg A_4
$$

has factors $L\cong C_2$, $V/L\cong C_2$, and $A_4/V\cong C_3$, since their orders are $2,2,3$. Each is simple because it has prime order, so the chain is a composition series. Each is also abelian, so this very chain satisfies the definition of solvability.

**Careful distinction.** The subgroup $L$ is normal in $V$, but not in $A_4$: a $3$-cycle conjugates its nonidentity element to a different double transposition. That does not invalidate the composition or solvable series; adjacent normality is the required condition.

**Technique:** find a small normal subgroup recognizable from cycle type, then refine it internally.

**Foundations:** @cu:algebra:midterm-2:proof-techniques:rk:permutation-method, @cu:algebra:midterm-2:definitions:df:simple-composition.
