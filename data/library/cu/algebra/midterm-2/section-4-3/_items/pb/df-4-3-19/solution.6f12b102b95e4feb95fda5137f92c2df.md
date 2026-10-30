Previous result:

Suppose $G$ acts transitively on a finite nonempty set $A$, and $H\nsubg G$. Let $O_1,\ldots,O_r$ be the $H$-orbits.

(a) $G$ permutes these orbits transitively, and all have equal cardinality.

(b) For $a\in O_1$, $|O_1|=[H:H\cap \Stab_G(a)]$ and $r=[G:H\Stab_G(a)]$.

---
Let $H\trianglelefteq G$, and let $K\subseteq H$ be a conjugacy class of $G$. Choose $x\in K$.

## (a) Prove that $K$ is a union of $k=[G:HC_G(x)]$ conjugacy classes of $H$, all of equal cardinality.

Consider the action of $G$ on $K$ by conjugation:
$$
\begin{aligned}
G\times K &\to K\\
(g,y)&\mapsto gyg^{-1}.
\end{aligned}
$$

Since $K$ is a conjugacy class of $G$, this action is transitive.

Now restrict the action to $H$. For any $y\in K$, the $H$-orbit of $y$ is
$$
\Orb_H(y)=\{hyh^{-1}:h\in H\},
$$
which is precisely the conjugacy class of $y$ in $H$.

Since $K\subseteq H$, every such orbit is a conjugacy class of $H$. Furthermore, the $H$-orbits partition $K$. Therefore,
$$
K=O_1\sqcup\cdots\sqcup O_k,
$$
where each $O_i$ is a conjugacy class of $H$.

By the previously established result for a normal subgroup acting on a transitive $G$-set, all $H$-orbits have equal cardinality.

It remains to determine the number $k$ of these orbits.

The stabilizer of $x$ under the conjugation action is
$$
\begin{aligned}
G_x
&=\{g\in G:gxg^{-1}=x\}\\
&=\{g\in G:gx=xg\}\\
&=C_G(x).
\end{aligned}
$$

By the previously established orbit-counting result, the number of $H$-orbits is
$$
k=[G:HG_x].
$$

Substituting $G_x=C_G(x)$ gives
$$
\boxed{k=[G:HC_G(x)]}.
$$

Therefore, $K$ is the disjoint union of exactly $k=[G:HC_G(x)]$ conjugacy classes of $H$, all of equal cardinality.

## (b) Deduce that a conjugacy class of $S_n$ consisting of even permutations is either a single conjugacy class of $A_n$ or a union of two conjugacy classes of $A_n$ of equal cardinality.

Let $G=S_n$ and $H=A_n$, where $n\ge 2$.

Since $A_n\trianglelefteq S_n$, we may apply part (a).

Let $K$ be a conjugacy class of $S_n$ consisting of even permutations, and choose $x\in K$.

Since every element of $K$ is even, we have $K\subseteq A_n$.

By part (a), $K$ is the disjoint union of
$$
k=[S_n:A_nC_{S_n}(x)]
$$
conjugacy classes of $A_n$, all of equal cardinality.

Observe that
$$
A_n\le A_nC_{S_n}(x)\le S_n.
$$

By multiplicativity of subgroup indices,
$$
[S_n:A_n]
=
[S_n:A_nC_{S_n}(x)]
[A_nC_{S_n}(x):A_n].
$$

Since $[S_n:A_n]=2$, we obtain
$$
2=k[A_nC_{S_n}(x):A_n].
$$

Both factors on the right are positive integers. Therefore,
$$
k\mid 2,
$$
so
$$
\boxed{k\in\{1,2\}}.
$$

Hence $K$ is either a single conjugacy class of $A_n$ or the disjoint union of two conjugacy classes of $A_n$ of equal cardinality.
