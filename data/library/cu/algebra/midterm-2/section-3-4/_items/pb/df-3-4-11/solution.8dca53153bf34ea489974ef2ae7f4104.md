Let $G$ be solvable and $1\ne H\nsubg G$. Prove there is a nontrivial abelian subgroup $A\le H$ with $A\nsubg G$.

Hint supplied in the request: prove that if $N\nsubg G$, then $[N,N]\nsubg G$.

## Show $N \nsubg G \implies [N,N]\nsubg G$.
Let $z\in [N,N]$.  Then $z$ can be written as
$$
z = [x,y] = x^{-1}y^{-1}xy.
$$
for $x,y\in G$.  Then
$$
gzg^{-1} = (gxg^{-1})^{-1} (gyg^{-1})^{-1} (gxg^{-1}) (gyg^{-1}) \in $[N,N]$.
$$
Therefore $[N,N]\nsubg G$.

## Show $A\le H$ with $A\nsubg G$.
Because $G$ is solvable, it has a derived series
$$
\set{\id_G} = G_0 \nsubg \cdots \nsubg G_n = G
$$
where $G_{k-1} = [G_k,G_k]$.

Note that $H$ also has a derived series $H_{k-1} = [H_k,H_k]$ and $H_n=H$.  Because $H$ is a subgroup of $G$, $[H_k,H_k]\subg G_k$.  Because the series for $G$ terminates, the series for $H$ terminates.  So $H$ is solvable.  Choose $A$ to be the smallest order element of the derived series for $H$.  Then $[A,A]=\id_G$ so $A$ is abelian and by the Lemma, $A$ is normal.
