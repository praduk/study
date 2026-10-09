A left action of $G$ on a set $A$ is a map $(g,a)\mapsto g\cdot a$ such that $1\cdot a=a$ and $(gh)\cdot a=g\cdot(h\cdot a)$. For $a\in A$,

$$
G\cdot a=\{g\cdot a:g\in G\},\qquad G_a=\{g:g\cdot a=a\}.
$$

The action is transitive if $A$ is nonempty and it is a single orbit. Its permutation representation is $\rho:G\to S_A$, $\rho(g)(a)=g\cdot a$; the kernel is $\bigcap_{a\in A}G_a$. It is faithful if this kernel is $1$.

For a subset $B\subseteq A$, the pointwise stabilizer consists of elements fixing every point of $B$. The setwise stabilizer is $\{g:gB=B\}$ and may permute points of $B$. In the lecture notation these are $\Stab_G(B)$ and $\WStab_G(B)$. In the assigned block problem, $G_B$ means the setwise stabilizer. For a single point the distinction disappears.

Do not confuse an action being transitive with being faithful. A nontrivial group acting on a singleton is transitive and has kernel equal to the whole group.
