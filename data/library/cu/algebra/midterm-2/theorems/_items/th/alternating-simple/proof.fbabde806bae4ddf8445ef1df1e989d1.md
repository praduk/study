**Base case: A₅.** The possible even cycle types on five points are identity, a double transposition, a $3$-cycle, and a $5$-cycle. In $S_5$ their class sizes are $1,15,20,24$, respectively: there are $5$ choices of the fixed point and $3$ pairings for double transpositions, $\binom53\cdot2=20$ $3$-cycles, and $4!=24$ $5$-cycles.

The double-transposition class remains one $A_5$-class because its centralizer contains an odd permutation, for example $(1\ 2)$ for $(1\ 2)(3\ 4)$. The $3$-cycle class also remains one class because the transposition of its two fixed points centralizes it. To justify this criterion, the splitting formula in 4.3.19 says the number of $A_5$-classes is $[S_5:A_5C_{S_5}(x)]$, which is $1$ exactly when the centralizer contains an odd element.

A permutation commuting with the $5$-cycle $c=(1\ 2\ 3\ 4\ 5)$ is determined by its value at $1$: commutation forces its value at $c^j(1)$ to be $c^j$ of that value. The five choices give exactly the powers of $c$, all even. Thus its centralizer is contained in $A_5$; the class splits into two equally sized $A_5$-classes, each of size $12$.

Hence the $A_5$ class sizes are $1,15,20,12,12$. A normal subgroup is a union of whole conjugacy classes and contains the identity. Its possible order is therefore $1$ plus a subset sum of $15,20,12,12$. The distinct possibilities are

$$
1,13,16,21,25,28,33,36,40,45,48,60.
$$

By Lagrange its order must also divide $60$. Among those listed, only $1$ and $60$ do. Thus $A_5$ has no nontrivial proper normal subgroup and is simple.

**Induction step.** Let $n\ge6$ and assume $A_{n-1}$ simple. Take a nontrivial $H\nsubg A_n$. For each point $i$, let $S_i$ be its stabilizer in $A_n$. Restricting to the other $n-1$ points identifies $S_i\cong A_{n-1}$, so $S_i$ is simple.

If some $1\ne h\in H$ fixes $i$, then $H\cap S_i$ is a nontrivial normal subgroup of $S_i$: it is normalized by $S_i$ because $H$ is normal in $A_n$. Simplicity forces $S_i\le H$. For every $j$, an even permutation sends $i$ to $j$ (for $i\ne j$ use a $3$-cycle through them and a third point). Conjugating then gives $S_j\le H$. Every $3$-cycle fixes some point when $n\ge6$, so it belongs to some $S_j$. As the $3$-cycles generate $A_n$, we obtain $H=A_n$.

It remains to rule out a proper nontrivial $H$ whose nonidentity elements fix no point. In such a subgroup, if $h,h'\in H$ agree at any point $a$, then $h^{-1}h'$ fixes $a$, so it must be identity; hence $h=h'$.

Take $1\ne h\in H$. If one cycle of $h$ has length at least $3$, name consecutive points $a_1,a_2,a_3$ in it. Choose distinct $d,e$ outside these three and set $\alpha=(a_3\ d\ e)\in A_n$. It fixes $a_1,a_2$ but moves $a_3$. The conjugate $h'=\alpha h\alpha^{-1}$ lies in $H$, agrees with $h$ at $a_1$ (both send it to $a_2$), and differs at $a_2$ (its image is $\alpha(a_3)\ne a_3$). This contradicts the agreement property.

Thus $h$ consists entirely of disjoint transpositions and has no fixed points. Because $h$ is even, the number of transpositions is even; with $n\ge6$, this forces at least four transpositions and in particular at least three. Name three as $(a_1\ a_2),(a_3\ a_4),(a_5\ a_6)$. Let $\alpha=(a_1\ a_2)(a_3\ a_5)\in A_n$. The conjugate $h'$ again lies in $H$. It still contains $(a_1\ a_2)$, so agrees with $h$ at $a_1$, but it sends $a_3$ to $a_6$ instead of $a_4$, since its relabeled pairs include $(a_5\ a_4)$ and $(a_3\ a_6)$. Hence $h'\ne h$, another contradiction. There is no proper nontrivial $H$, completing simplicity.

Finally $A_n$ is nonabelian: the $3$-cycles $(1\ 2\ 3)$ and $(1\ 2\ 4)$ do not commute (their products send $1$ to different points). This works for every $n\ge5$.

**Technique:** the lecture proof first uses the $A_5$ class equation, then point stabilizers and conjugates agreeing at one point. The key induction step needs both normality of $H$ and simplicity of each smaller point stabilizer.
