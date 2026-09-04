An occurrence of $x$ in $∀xφ$ or $∃xφ$ is bound when it lies in the scope of that displayed quantifier; an occurrence not governed by a matching quantifier is free. Write $FV(φ)$ for the set of variables having a free occurrence in $φ$. Recursively, atomic formulas inherit the variables in their terms, connectives take unions, and $FV(Qxφ)=FV(φ)\setminus\{x\}$ for $Q∈\{∀,∃\}$.

A variable can have both free and bound occurrences in one formula. For example, the first $x$ is free and the second is bound in $P(x)∧∀xQ(x)$.
