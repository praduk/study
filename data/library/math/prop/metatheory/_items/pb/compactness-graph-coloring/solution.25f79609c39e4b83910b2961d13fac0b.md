For each $v\in V$ and color $i\in\{1,\ldots,k\}$, use an atom $p_{v,i}$ meaning that vertex $v$ has color $i$. Countability of $V$ and finiteness of the color set make these atoms countable, so reindex them into the fixed stock $p_0,p_1,\ldots$.

For each vertex $v$, define a right-associated finite disjunction recursively by

$$D_{v,k}=p_{v,k},\qquad D_{v,i}=(p_{v,i}\lor D_{v,i+1})\quad(1\leq i<k).$$

Thus $D_{v,1}$ is the precise formula abbreviated by $\bigvee_{i=1}^k p_{v,i}$; the assumption $k\geq1$ avoids an empty disjunction. Let $\Gamma$ contain:

- $D_{v,1}$ for each vertex $v$;
- $(\neg p_{v,i}\lor\neg p_{v,j})$ for each vertex $v$ and distinct colors $i,j$;
- $(\neg p_{u,i}\lor\neg p_{v,i})$ for each edge $\{u,v\}\in E$ and each color $i$.

The first family assigns at least one color, the second at most one, and the third different colors to adjacent vertices. Any finite $\Gamma_0\subseteq\Gamma$ mentions only finitely many vertices $W$. By hypothesis, the finite induced graph on $W$ has a proper $k$-coloring. Assign the corresponding atoms and extend arbitrarily to all other atoms; this valuation satisfies $\Gamma_0$. Hence every finite subset of $\Gamma$ is satisfiable. Compactness gives a valuation satisfying all of $\Gamma$, and the unique true color atom for each vertex defines a proper $k$-coloring of $G$.
