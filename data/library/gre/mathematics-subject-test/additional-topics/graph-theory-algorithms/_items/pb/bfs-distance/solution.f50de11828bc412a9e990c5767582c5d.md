**Answer.** $2$.

**Pattern cue.** Explore distance layers.

**Fast route.** Layer one contains $a,b$; $d$ is adjacent to $b$, so it appears in layer two via $s-b-d$. No edge $sd$ exists, so the distance cannot be one.

**Trap.** A DFS route $s-a-c-d$ has three edges and need not be shortest.

**Recall.** @gre:mathematics-subject-test:additional-topics:graph-theory-algorithms:rk:bfs-dfs.
