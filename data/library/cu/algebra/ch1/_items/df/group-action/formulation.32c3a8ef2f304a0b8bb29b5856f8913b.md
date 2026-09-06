A group $G$ *acts* on a set $A$ if there exists a homomorphism
$$
\phi:G\to S_A.
$$

A *left action* of a $G$ on $A$ is a function
$$
\phi:G\times A\to A
$$
such that
1. For each $a\in A$, $\phi(1_G,a)=a$.
2. For each $g,h\in G$ and for each $a\in A$, $\phi(gh,a) = \phi(g,\phi(h,a)).$

A group action is *faithful* if for each $g\in G$,
$$
\forall a\in A, g(a)=a \implies g=\id_G.
$$
