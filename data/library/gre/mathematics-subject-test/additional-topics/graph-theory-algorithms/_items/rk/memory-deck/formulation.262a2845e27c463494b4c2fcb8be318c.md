## Graph invariants

For a finite undirected graph,

$$
\sum_{v\in V}\deg v=2|E|,
$$

so the number of odd-degree vertices is even. A complete graph has $\binom n2$ edges. A tree on $n$ vertices has $n-1$ edges and a unique simple path between each pair of vertices.

A connected graph has an Euler circuit iff every vertex has even degree; it has an open Euler trail iff exactly two vertices have odd degree. Hamiltonian paths concern visiting vertices once and obey different criteria.

A graph is bipartite iff it has no odd cycle. A planar connected graph satisfies

$$
|V|-|E|+|F|=2,
$$

and for a simple planar graph with $|V|\ge3$, $|E|\le3|V|-6$.

## Traversal and shortest paths

Breadth-first search on an unweighted graph finds minimum-edge-distance paths and runs in $O(|V|+|E|)$ with adjacency lists. Depth-first search supports cycle detection, connected components, topological ordering of a DAG, and articulation analysis.

Dijkstra's algorithm requires nonnegative edge weights. Topological sort exists exactly for directed acyclic graphs.

## Complexity anchors

$$
1<\log n<n<n\log n<n^2<n^3<2^n<n!
$$

asymptotically. Binary search is $O(\log n)$. Comparison sorting has a worst-case lower bound $\Omega(n\log n)$; mergesort is $O(n\log n)$, while insertion sort is $O(n^2)$ in the worst case.

Common recurrence patterns:

$$
T(n)=T(n/2)+O(1)=O(\log n),
$$

$$
T(n)=2T(n/2)+O(n)=O(n\log n).
$$

## Recognition traps

Tree, Eulerian, Hamiltonian, planar, and bipartite are different properties. $O(g)$ is an upper bound, $\Omega(g)$ a lower bound, and $\Theta(g)$ a two-sided asymptotic bound. Runtime claims depend on the graph representation.
