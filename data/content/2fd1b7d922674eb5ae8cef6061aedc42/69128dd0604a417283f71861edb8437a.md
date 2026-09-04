The outermost constructor is the displayed disjunction: its left disjunct is $∀x(P(x)→∃y(R(x,y)∧Q(y)))$ and its right disjunct is $S(x)$. The occurrences of $x$ in $P(x)$ and $R(x,y)$ are bound by $∀x$; the $y$ occurrences in $R(x,y)$ and $Q(y)$ are bound by $∃y$; the final $x$ in $S(x)$ is free because it lies outside the scope of $∀x$.

The requested reading is $∀x((P(x)→∃y(R(x,y)∧Q(y)))∨S(x))$. Now every occurrence of $x$ is bound by the universal quantifier, while both occurrences of $y$ remain bound by the existential quantifier.
