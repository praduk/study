**Answer.** $2n-1$.

**Pattern cue.** Count the nodes of a full binary recursion tree or solve by induction.

**Fast route.** There are $n$ leaves and $n-1$ internal nodes, each of unit cost. Alternatively $2[2(n/2)-1]+1=2n-1$.

**Trap.** There are logarithmically many levels, but exponentially more nodes on deeper levels.

**Recall.** @gre:mathematics-subject-test:additional-topics:graph-theory-algorithms:rk:runtime-recurrences.
