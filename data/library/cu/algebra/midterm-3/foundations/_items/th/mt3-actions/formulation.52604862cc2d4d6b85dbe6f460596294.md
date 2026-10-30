An **action** of $G$ on $X$ is a homomorphism $G\to\Sym(X)$. The orbit of $x$ is $Gx$ and its stabilizer is $G_x=\{g:gx=x\}$. Orbit–stabilizer gives $|Gx|=|G:G_x|$.

**Fixed-point congruence.** If a finite $p$-group $P$ acts on a finite set $X$, then

$$
|X|\equiv |X^P|\pmod p,
$$

where $X^P=\{x:gx=x\text{ for all }g\in P\}$. In particular, $p\nmid|X|$ forces a fixed point.

**Coset action.** For $H<G$ of finite index $m$, left multiplication on $G/H$ gives $G\to S_m$ with kernel $\bigcap_{g\in G}gHg^{-1}\le H$, called the **core**. If $G$ is simple, this nontrivial transitive action is faithful, so $G\hookrightarrow S_m$. If $G$ is nonabelian simple, its sign map is trivial, so $G\hookrightarrow A_m$ and $|G|\mid m!/2$ for $m\ge2$.

**Triggers:** few Sylow subgroups → conjugation action; small-index subgroup → coset action; a $p$-group acting on a set of size prime to $p$ → fixed point. A fixed Sylow subgroup is invariant under the acting group, not necessarily pointwise fixed.

The **left regular action** of a finite group on itself is $g\cdot x=gx$; it is faithful. A permutation is **even** when its sign is $+1$; a product of $k$ transpositions has sign $(-1)^k$. A permutation of order $p$ is a product of disjoint $p$-cycles and fixed points. The exponent of $p$ in $n!$ is $\sum_{j\ge1}\lfloor n/p^j\rfloor$, obtained by counting one factor $p$ for each multiple of $p$, another for each multiple of $p^2$, and so on.

**Index two implies normal.** The action on the two cosets of $H$ has transitive image $S_2$, so its kernel has index2 and lies in $H$. It must equal $H$, which is therefore normal.
