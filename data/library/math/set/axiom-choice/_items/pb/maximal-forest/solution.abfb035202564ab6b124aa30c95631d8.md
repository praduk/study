Fix an acyclic $F_0\subseteq E$ and let

$$
P=\{F:F_0\subseteq F\subseteq E\text{ and }F\text{ is acyclic}\},
$$

ordered by inclusion. If $\mathcal C$ is a chain in $P$, its union $U=\bigcup\mathcal C$ contains $F_0$. It is acyclic: any cycle uses only finitely many edges; because $\mathcal C$ is linearly ordered by inclusion, all those finitely many edges would lie in one member of $\mathcal C$, contradicting its acyclicity. Thus $U\in P$ and is an upper bound. Zorn's Lemma gives a maximal $F\in P$.

Now suppose $G$ is connected. The spanning subgraph $(V,F)$ is a forest. If it were disconnected, choose vertices $u,v$ in different $F$-components. A finite $G$-path from $u$ to $v$ has a first edge $e$ crossing between two $F$-components. Adding $e$ cannot create a cycle, because a cycle would provide an $F$-path between its endpoints. Hence $F\cup\{e\}$ is acyclic, contradicting maximality. Therefore $(V,F)$ is connected and acyclic: it is a spanning tree.
