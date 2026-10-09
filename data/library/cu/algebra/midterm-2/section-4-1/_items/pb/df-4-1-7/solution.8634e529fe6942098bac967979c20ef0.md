**(a) Setwise stabilization.** The identity stabilizes $B$. If $gB=B$ and $hB=B$, then $h^{-1}B=B$ and $gh^{-1}B=B$, proving $G_B\le G$. If $g\in G_a$, then $a=g(a)\in gB\cap B$. Since $B$ is a block, this nonempty intersection forces $gB=B$. Hence $G_a\le G_B$.

**(b) The translates form a partition.** If $gB\cap hB\ne\varnothing$, apply $h^{-1}$ to get $(h^{-1}g)B\cap B\ne\varnothing$. The block condition yields $(h^{-1}g)B=B$, so $gB=hB$. Thus distinct translates are disjoint. They cover $A$ because, fixing $a\in B$, transitivity supplies for each $b\in A$ some $g$ with $g(a)=b$, whence $b\in gB$.

**(c) The two examples.** Suppose $B$ is a block for $S_4$ with $1<|B|<4$. Choose distinct $a,b\in B$ and $c\notin B$. The transposition $(b\ c)$ fixes $a$, so its translate of $B$ intersects $B$, but the translate contains $c$ and is not $B$. This contradicts the block condition. Hence only trivial blocks exist. For $D_8$, label square vertices $1,2,3,4$ cyclically. The opposite pair $\{1,3\}$ is sent by every square symmetry either to itself or to the disjoint opposite pair $\{2,4\}$. It is a nontrivial block.

**(d) Maximal stabilizers imply primitivity.** Assume $|A|>1$ and $G_a$ maximal. For a block $B$ containing $a$, part (a) gives $G_a\le G_B\le G$, so $G_B=G_a$ or $G_B=G$. If $G_B=G$, transitivity and invariance of $B$ imply $B=A$. If $G_B=G_a$, let $b\in B$ and choose $g$ with $g(a)=b$. Then $gB$ intersects $B$ at $b$, so $g\in G_B=G_a$ and $b=a$. Thus $B=\{a\}$. Any block can be treated by choosing a point it contains.

**Primitivity implies maximal stabilizers.** Let $G_a\le K\le G$ and set $B=K\cdot a$. To prove $B$ is a block, suppose $gB\cap B\ne\varnothing$. Then $gk_1(a)=k_2(a)$ for some $k_1,k_2\in K$. Thus $k_2^{-1}gk_1\in G_a\le K$, implying $g\in K$ and hence $gB=B$. Primitivity forces $B=\{a\}$ or $A$. In the first case every $k\in K$ fixes $a$, so $K=G_a$. In the second case, for arbitrary $g\in G$, choose $k\in K$ with $k(a)=g(a)$. Then $k^{-1}g\in G_a\le K$, so $g\in K$. Hence $K=G$. For $|A|>1$, transitivity makes $G_a<G$, so this is maximality.

**Boundary in the textbook wording.** The equivalence in (d) needs $|A|>1$. On a singleton the action is primitive according to the definition, but $G_a=G$ is not a proper, hence not a maximal, subgroup. Parts (a)–(c) have no such problem. The proof above states the missing boundary condition explicitly.

**Technique:** an intersecting translate forces a block to be invariant. Overgroups of a stabilizer correspond to blocks through its point.

**Foundations:** @cu:algebra:midterm-2:theorems:th:orbit-stabilizer, @cu:algebra:midterm-2:definitions:df:action-stabilizer.
