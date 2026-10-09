Suppose $N$ is a nontrivial abelian subgroup of $G$, minimal among nontrivial normal subgroups of $G$ contained in $N$. Let $H<G$ satisfy $NH=G$. Prove $N\cap H=1$ and $H$ is a maximal subgroup of $G$.

# Show $N\cap H = 1_G$.

Let $x\in H\cap N$.  Let $h\in H$.  Then $hxh^{-1}\in N$ because $N\nsubg G$ and $hxh^{-1}\in H$ because $x\in H$.  So $hxh^{-1}\in H\cap N$ and $H\cap N\nsubg H$.

Because $N$ is abelian, $H \cap N$ is also normal in $N$.

Because $G=NH$, every $g\in G$ can be written as $g=nh$ for some $n\in N$ and $h\in H$.  Therefore for every $x\in H\cap N$,

$$
gxg^{-1} = n\underbrace{(hxh^{-1})}_{\in N\cap H}n^{-1} \in N\cap H.
$$

Therefore, $N\cap H$ is normal in $G$.  But because $N$ is the minimal nontrivial normal subgroup, $N\cap H=\set{1_G}$.

# Show $H$ is a maximal subgroup of $G$.
Suppose $H\le K < G$.  Because $NH=G$, and $H\le K$, $NK=G$. By the same argument as above replacing $K$ with $H$, $N\cap K=1$.

By second isomorphism theorem, $G/N \isoto H/H\cap N$ and $G/N \isoto K/K\cap N$.
