**Answer.** Bellman–Ford.

**Pattern cue.** Negative edges remove Dijkstra’s standard guarantee.

**Fast route.** Bellman–Ford repeatedly relaxes all edges and handles negative weights; the stated absence of reachable negative cycles allows finite shortest paths for reachable vertices.

**Trap.** A particular Dijkstra run might succeed, but the general guarantee is absent.

**Recall.** @gre:mathematics-subject-test:additional-topics:graph-theory-algorithms:rk:weighted-paths.
