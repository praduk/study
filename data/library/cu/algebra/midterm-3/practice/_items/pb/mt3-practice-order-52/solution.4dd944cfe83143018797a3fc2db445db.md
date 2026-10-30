**Strategy:** Force a normal Sylow subgroup, find a complement, classify its actions, identify changes of generators, and distinguish the surviving groups by invariants. This is the @[semidirect classification method]cu:algebra:midterm-3:semidirect:rk:mt3-classify.

**Definitions and results used:** @[Sylow theorem]cu:algebra:midterm-3:sylow:th:mt3-sylow; @[Unique Sylow subgroups are normal]cu:algebra:midterm-3:sylow:th:mt3-sylow-normality; @[Lagrange’s theorem]cu:algebra:midterm-3:foundations:th:mt3-lagrange; @[Subgroup-product order formula]cu:algebra:midterm-3:foundations:th:mt3-subgroup-product; @[Groups of order p²]cu:algebra:midterm-3:sylow:th:mt3-p-square-abelian; @[Semidirect product definition]cu:algebra:midterm-3:semidirect:df:mt3-semidirect; @[Construction and internal recognition]cu:algebra:midterm-3:semidirect:th:mt3-semidirect-recognition; @[Cyclic automorphisms]cu:algebra:midterm-3:foundations:th:mt3-cyclic-automorphisms; @[Cyclic actions]cu:algebra:midterm-3:semidirect:th:mt3-cyclic-actions; @[First isomorphism theorem]cu:algebra:midterm-3:foundations:th:mt3-first-isomorphism; @[Center]cu:algebra:midterm-3:foundations:df:mt3-center.

**(a), step 1: force the normal factor.** Sylow gives

$$
n_{13}\mid4,\qquad n_{13}\equiv1\pmod{13}.
$$

The divisors $1,2,4$ leave only $n_{13}=1$. Thus the unique Sylow $13$-subgroup $A$ is normal. Any nonidentity element $a\in A$ has order $13$ by Lagrange, so $A=\langle a\rangle\cong C_{13}$.

**Step 2: find a complement.** Let $Q$ be a Sylow $2$-subgroup, so $|Q|=4$. The order of $A\cap Q$ divides both $13$ and $4$, hence $A\cap Q=1$. The subgroup-product formula gives

$$
|AQ|=\frac{|A||Q|}{|A\cap Q|}=52,
$$

so $AQ=G$. Internal semidirect recognition now gives

$$
G\cong A\semid_\varphi Q,\qquad
\varphi(q)(a)=qaq^{-1}.
$$

A group of order $2^2$ is $C_4$ or $C_2\times C_2$. This proves (a). The normal factor is $A$; $Q$ need not be normal.

**(b), step 3: classify the actions when $Q=C_4$.** Write $Q=\langle b\rangle$. An automorphism of $A$ has the form $a\mapsto a^r$, where $r$ is a nonzero residue modulo $13$. Since $b^4=1$, the action must satisfy $r^4\equiv1\pmod{13}$.

The permitted fact $\Aut(C_{13})\cong C_{12}$ says its elements of order dividing $4$ form its unique subgroup of order $4$. Explicitly,

$$
5^2\equiv-1\pmod{13},\qquad 5^3\equiv8\pmod{13},\qquad5^4\equiv1\pmod{13},
$$

so the four possibilities are $r=1,12,5,8$. They have orders $1,2,4,4$, respectively. Let

$$
G_r=C_{13}\semid_{\varphi_r}C_4,\qquad
\varphi_r(b)(a)=a^r.
$$

Its elements have unique forms $a^ib^j$, with $0\le i<13$ and $0\le j<4$. The cases are:

- $r=1$: the action is trivial, giving $G_1=C_{13}\times C_4\cong C_{52}$. The pair of generators has order $52$, since a power killing it must be divisible by both $13$ and $4$.
- $r=12=-1$: $b$ acts by inversion. This gives $G_{12}=C_{13}\semid C_4$ with $bab^{-1}=a^{-1}$; the action has kernel $\langle b^2\rangle$.
- $r=5$ or $8$: the action is faithful, since the image of $b$ has order $4$. These two formulas give one isomorphism type. Replacing $b$ by the equally valid generator $b^{-1}$ replaces $r$ by $r^{-1}$, and $5^{-1}\equiv8\pmod{13}$. Explicitly, from $G_5$ to $G_8$, send $a\mapsto a'$ and $b\mapsto(b')^{-1}$; the images have the required orders, satisfy the same conjugation rule, and generate $G_8$. Unique normal forms, or the inverse assignment, give an isomorphism.

Changing the generator $a$ does not introduce a further case: for any nonzero $u\pmod{13}$,

$$
b(a^u)b^{-1}=a^{ru}=(a^u)^r.
$$

Thus there are at most three types with cyclic Sylow $2$-subgroups, represented by $G_1,G_{12},G_5$.

**Step 4: classify the actions when $Q=C_2\times C_2$.** Every $q\in Q$ satisfies $q^2=1$, so every $\varphi(q)$ has order at most $2$. A cyclic group of order $12$ has only one element of order $2$, namely the inversion automorphism $a\mapsto a^{-1}$. Consequently $\im\varphi$ is either trivial or that order-$2$ subgroup.

For the trivial action, obtain

$$
C_{13}\times C_2\times C_2\cong C_{26}\times C_2.
$$

For a nontrivial action, the first isomorphism theorem gives $|\ker\varphi|=4/2=2$. Choose $c$ generating the kernel and choose $b\notin\ker\varphi$. Then $b,c$ are distinct involutions and generate $Q$; their actions are

$$
bab^{-1}=a^{-1},\qquad cac^{-1}=a,\qquad bc=cb.
$$

Every nontrivial homomorphism admits such a choice of $b,c$. Therefore the three possible kernel subgroups do not produce three types: relabeling the generators of $Q$ sends any such adapted pair to another.

The subgroup $\langle a,b\rangle$ is $C_{13}\semid C_2=D_{26}$, the dihedral group of order $26$, using the guide’s @[dihedral convention]cu:algebra:midterm-3:foundations:rk:mt3-notation. The subgroup $\langle c\rangle$ commutes with it. Their intersection is trivial by the unique expressions $a^ib^jc^k$ with $0\le i<13$ and $j,k\in\{0,1\}$, and together they generate $G$. Hence

$$
G\cong D_{26}\times C_2.
$$

**Step 5: verify existence and completeness.** Each action just listed is a homomorphism: in the $C_4$ cases the chosen automorphism has order dividing $4$; in the $C_2^2$ cases the two chosen commuting automorphisms have orders dividing $2$. The external semidirect construction therefore produces an actual group with underlying set $C_{13}\times Q$, of exactly $13\cdot4=52$ elements, in every case. Part (a) and the exhaustive action lists prove that every group of order $52$ occurs on this list. It remains to prove that the five representatives are pairwise nonisomorphic.

**Step 6: compute the centers instead of guessing them.** For $G_r$, let $g=a^ib^j$. Since $a,b$ generate the group, $g\in Z(G_r)$ exactly when it commutes with both. Compare

$$
ga=a^{i+r^j}b^j,\qquad ag=a^{i+1}b^j,
$$

and

$$
bg=a^{ri}b^{j+1},\qquad gb=a^ib^{j+1}.
$$

The unique normal forms show that the two centrality conditions are precisely

$$
r^j\equiv1\pmod{13},\qquad (r-1)i\equiv0\pmod{13}.
$$

For $r=1$, both conditions always hold, so the center is the whole group. For $r=-1$, the second condition forces $i=0$ and the first forces $j$ even; thus $Z(G_{12})=\langle b^2\rangle$ has order $2$. For $r=5$, the second again forces $i=0$, while $5$ has order $4$, so $j=0$ modulo $4$; thus $Z(G_5)=1$.

The trivial $C_2^2$ action is abelian, so its center has order $52$. In the nontrivial case, write $g=a^ib^jc^k$. Commutation with $a$ forces $j=0$, since $b$ inverts $a$. Commutation with $b$ then forces $a^i=a^{-i}$, hence $2i\equiv0\pmod{13}$ and $i=0$. The element $c$ commutes with both generators. Therefore the center is exactly $\langle c\rangle$, of order $2$.

**Step 7: separate all five types.** An isomorphism sends a Sylow $2$-subgroup to a Sylow $2$-subgroup; Sylow conjugacy ensures that the subgroup type does not depend on which one was chosen. Thus a cyclic Sylow $2$-subgroup distinguishes the first three groups from the last two. Isomorphisms also preserve the center, because they preserve commutation with every group element. The computed center orders distinguish the groups within each of those two classes:

| Group | Sylow $2$-subgroup | Center order |
| --- | --- | --- |
| $C_{52}$ | $C_4$ | $52$ |
| $C_{13}\semid C_4$, $bab^{-1}=a^{-1}$ | $C_4$ | $2$ |
| $C_{13}\semid C_4$, $bab^{-1}=a^5$ | $C_4$ | $1$ |
| $C_{26}\times C_2$ | $C_2\times C_2$ | $52$ |
| $D_{26}\times C_2$ | $C_2\times C_2$ | $2$ |

These are exactly the five isomorphism types.

**Exam proof cue:** Normal Sylow factor $\to$ complement $\to$ action images $\to$ change generators $\to$ Sylow type and center. Do not count two action formulas as distinct groups until an invariant separates them.

**Provenance:** Original practice adapted from the classification method in @[Dummit–Foote §5.5, Exercise 12]cu:algebra:midterm-3:hw1:pb:mt3-hw1-df-5-5-12 (groups of order $20$). The order-$52$ calculation above is independently derived.
