“Every $P$ is $Q$” is rendered as $∀x(P(x)→Q(x))$, while “some $P$ is $Q$” is $∃x(P(x)∧Q(x))$. Replacing the implication in the universal translation by conjunction would wrongly assert that everything is a $P$.

The abbreviation $∃!xφ(x)$ means that exactly one object satisfies $φ$. One expansion is $∃x(φ(x)∧∀y(φ(y)→y=x))$, where $y$ is fresh. This asserts both existence and at most one witness; $∀x∀y((φ(x)∧φ(y))→x=y)$ alone asserts only uniqueness at most.

Quantifier negations obey $¬∀xφ↔∃x¬φ$ and $¬∃xφ↔∀x¬φ$. Quantifier order generally cannot be exchanged: $∀x∃yR(x,y)$ permits a witness depending on $x$, whereas $∃y∀xR(x,y)$ demands one common witness.
