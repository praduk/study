Let $N$ be a finite subgroup of $G$ and $N=\langle S\rangle$ for a subset $S$. Prove that $g\in G$ normalizes $N$ if and only if $gSg^{-1}\subseteq N$.

# $\implies$
Supose $g$ normalizes $N$, that is $g\in N_G(N)$.  From the definition of @[normalizer]normalizer
$$
g\in N_G(N) \iff \forall n\in N, gng^{-1} \in N \iff gNg^{-1}\subseteq N.
$$
Because $S$ is a subset of $N$, $gSg^{-1} \subseteq N$.

# $\impliedby$
Suppose $gSg^{-1}\subseteq N$.  Let $n\in N$.  We can write $n$ as a product of elements in $S$
$$
n = s_1 s_2 \cdots s_k.
$$
Then
$$
gng^{-1} = (gs_1g^{-1})(gs_2g^{-1}) \cdots (g s_k g^{-1}).
$$
Because each of the factors above are in $N$, $gng^{-1}\in N$.  Therefore
$$
g\in N_G(N).
$$
