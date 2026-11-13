A poset $P$ on a set $A$ is a subset of $A\times A$ (a relation), such that for
all $x,y,z\in A$,

1. (reflexive) $(x,x)\in P$
2. (anti-symmetric) $(x,y),(y,x)\in P \implies x=y$
3. (transitive) $(x,y)\in P,(y,z)\in P \implies (x,z)\in P$

A chain is a subset $C\subseteq P$ such that for all $x,y\in C$, $(x,y)\in C$ or $(y,x)\in C$.  A chain is bounded by $b\in A$ if for all $x\in C$, $(x,b)\in C$.

Zorn's Lemma states that if every chain in $P$ is bounded, then $P$ has a maximal element.  A maximal element is an element $p\in P$ the bound is contained in $P$.
