**Correct choice: (B).**

**Fastest valid route.** Breadth-first search processes vertices in layers of increasing edge distance from $s$. With adjacency lists, every vertex is initialized or visited once and every undirected edge is examined at most twice, giving $O(n+m)$ time.

**Verification.** When a vertex is first discovered by breadth-first search, any path with fewer edges would have had to reach it from an earlier layer, so the recorded distance is minimal. Depth-first paths need not be shortest. Dijkstra requires nonnegative weights. Kruskal minimizes the total weight of a spanning tree rather than distances from a root. Choice (E) describes an adjacency-matrix-style bound, not the adjacency-list bound.
