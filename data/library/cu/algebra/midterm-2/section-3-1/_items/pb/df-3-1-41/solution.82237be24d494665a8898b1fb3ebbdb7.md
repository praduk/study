#### Show that generators of $N$ conjugate to another generator.
Let $n$ be a generator of $G$.  So there exist $x,y\in G$ such that $n=x^{-1}y^{-1}xy$.
But then for some $g\in G$
$$
\align{
gng^{-1} &= gx^{-1}y^{-1}xyg^{-1} \\
&= (gxg^{-1})^{-1} (gyg^{-1})^{-1} (gxg^{-1}) (gyg^{-1})
}
$$
Therefore $gng^{-1}$ is a generator of $N$.

For every $m\in N$, we can write it as a product of generators
$$
m = n_0 n_1 \ldots n_k.
$$
But then for every $g\in G$,
$$
gmg^{-1} = (gn_0g^{-1})(gn_1g^{-1}) \cdots (gn_kg^{-1}) \in N.
$$
Therefore $N \nsubg G$.

#### Show $G/N$ is abelian

Let $g_1,g_2\in G$.  Then
$$
(g_1N) (g_2N) = g_1g_2N = g_1g_2g_2^{-1}g_1^{-1}g_1g_2 N = g_1g_2 N = (g_1N)(g_2N).
$$
