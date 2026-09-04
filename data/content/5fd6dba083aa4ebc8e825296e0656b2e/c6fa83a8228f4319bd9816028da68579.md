Assume Choice and let $A$ be nonempty. Fix a choice function $c$ on the nonempty subsets of $A$. By transfinite recursion through the Hartogs ordinal $h(A)$, choose

$$
f(\alpha)=c\bigl(A\setminus f[\alpha]\bigr)
$$

whenever the displayed remainder is nonempty; after it becomes empty, use any fixed element of $A$ merely to keep the recursion total. Before exhaustion, the selected values are distinct. If exhaustion never occurred below $h(A)$, $f$ would inject $h(A)$ into $A$, contradicting Hartogs' theorem. Hence there is a least $\beta<h(A)$ with $f[\beta]=A$. Then $f\mathbin{\upharpoonright}\beta:\beta\to A$ is a bijection, and transporting the ordinal order on $\beta$ well-orders $A$. The empty set is well-ordered by the empty relation.

Conversely, assume every set can be well-ordered. Given a set $\mathcal A$ of nonempty sets, well-order $U=\bigcup\mathcal A$. For each $A\in\mathcal A$, let $c(A)$ be the least element of $A$ in this well-order. Replacement produces the graph of $c$, and $c$ is a choice function. Thus Choice holds.
