## Core facts

For a finite undirected graph, the handshake lemma says

$$
\sum_{v\in V}\deg(v)=2|E|.
$$

A tree is equivalently a connected acyclic graph; a tree with $n$ vertices has $n-1$ edges, and adding one edge creates exactly one cycle. A graph is bipartite exactly when it has no odd cycle. An undirected connected graph has an Euler circuit exactly when every vertex has even degree, and it has an Euler trail with distinct endpoints exactly when precisely two vertices have odd degree. These are statements about using every edge, not every vertex.

For a connected planar embedding, Euler's formula is $|V|-|E|+|F|=2$. With $c$ components it becomes $|V|-|E|+|F|=1+c$. A simple planar graph with at least three vertices satisfies $|E|\le3|V|-6$; a simple bipartite planar graph with at least three vertices satisfies the sharper $|E|\le2|V|-4$. These bounds are necessary, not sufficient, for planarity.

Breadth-first search explores an unweighted graph by distance layers and finds minimum-edge paths from its source. Depth-first search is useful for components, cycle detection, and topological ordering, but its search-tree paths need not be shortest. With adjacency lists, both run in $O(|V|+|E|)$ time.

Dijkstra's algorithm requires nonnegative edge weights. Bellman--Ford accommodates negative weights and detects reachable negative cycles. Kruskal's and Prim's algorithms produce minimum spanning trees, not shortest-path trees. Binary search is $O(\log n)$ on indexed sorted data; comparison sorting requires $\Omega(n\log n)$ comparisons in the worst case. Know basic recurrence growth and the distinction among best, average, and worst case.

## Recognition cues

- “Fewest edges” in an unweighted graph signals breadth-first search.
- Degree sums turn local information into the edge count.
- For planar questions, determine connectedness and face-length restrictions before applying a formula.
- Distinguish visiting all edges, visiting all vertices, shortest paths, and minimum total tree weight.

## Edge cases and traps

- A disconnected acyclic graph is a forest, not a tree.
- A graph can satisfy $|E|\le3|V|-6$ and still be nonplanar.
- Negative edges invalidate Dijkstra's guarantee even when a particular run happens to succeed.
- Big-$O$ is an upper-bound class, not automatically a tight bound.
- Adjacency-matrix traversal may cost $\Theta(|V|^2)$ even when the graph is sparse.
