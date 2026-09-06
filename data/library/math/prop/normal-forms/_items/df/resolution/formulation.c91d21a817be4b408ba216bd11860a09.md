Treat a clause as a finite set of literals. If $C\cup\{p\}$ and $D\cup\{\neg p\}$ are clauses, their **resolvent on $p$** is

$$C\cup D.$$

The inference from the two parent clauses to this resolvent is the **resolution rule**. A **resolution derivation** from a clause set $S$ is a finite sequence in which each clause is in $S$ or is a resolvent of earlier clauses. A **resolution refutation** derives the empty clause $\varnothing$, whose disjunction is $\false$. Tautological clauses containing both $p$ and $\neg p$ may be discarded because every valuation satisfies them.
