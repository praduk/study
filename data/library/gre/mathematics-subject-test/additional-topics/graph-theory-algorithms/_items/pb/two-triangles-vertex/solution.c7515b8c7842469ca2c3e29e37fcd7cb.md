**Answer.** Euler circuit: yes. Hamiltonian cycle: no.

**Pattern cue.** Separate edge parity from the effect of a cut vertex.

**Fast route.** The shared vertex has degree four and the other four vertices degree two, so an Euler circuit exists. A Hamiltonian cycle would need to enter and leave both triangles through the shared vertex, visiting it more than once.

**Trap.** An Eulerian graph need not be Hamiltonian.

**Recall.** @gre:mathematics-subject-test:additional-topics:graph-theory-algorithms:th:euler-trails.
