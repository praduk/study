**(a) Conjugacy classes are mapped onto conjugacy classes.** If $\alpha\in\operatorname{Aut}(G)$, then

$$
\alpha(gxg^{-1})=\alpha(g)\alpha(x)\alpha(g)^{-1}.
$$

As $g$ runs through $G$, $\alpha(g)$ also runs through $G$ because $\alpha$ is surjective. Therefore $\alpha(\operatorname{Cl}_G(x))=\operatorname{Cl}_G(\alpha(x))$. The restriction of $\alpha$ is a bijection of these classes, so their sizes agree.

**(b) Compare the involution classes by counting.** An involution in $S_n$ is a product of $r$ disjoint transpositions, with $1\le r\le\lfloor n/2\rfloor$. The number with this cycle type is

$$
c_r=\frac{n!}{2^r r!(n-2r)!}.
$$

To derive it, order $2r$ distinct points in $n!/(n-2r)!$ ways, pair successive points, and divide by $2^r$ for the order within each pair and by $r!$ for the order of the pairs. The transposition class has $c_1=n(n-1)/2$ elements. Equality $c_r=c_1$ for $r\ge2$ is equivalent to

$$
\frac{(n-2)!}{(n-2r)!}=2^{r-1}r!.
$$

For $r=2$, this would mean $(n-2)(n-3)=4$. At $n=4$ the left side is $2$ and at $n=5$ it is $6$; it increases thereafter, so equality never occurs. For $r=3$, the smallest permitted $n$ is $6$, where the left side is $4!=24=2^2\cdot3!$. It strictly increases for $n>6$, so equality occurs only at $n=6$. For $r\ge4$, at the smallest permitted $n=2r$ the ratio of the left side to the right side is

$$
R_r=\frac{(2r-2)!}{2^{r-1}r!}.
$$

Here $R_4=720/192>1$, and

$$
\frac{R_{r+1}}{R_r}=\frac{(2r)(2r-1)}{2(r+1)}>1\qquad(r\ge4).
$$

Thus $R_r>1$ for all $r\ge4$; increasing $n$ only increases the left side. There are no more equalities. Since $n\ne6$, the transposition class is the unique involution class of its size. Part (a) and order preservation force every automorphism to send transpositions to transpositions.

**(c) Show the images form a star.** Put $t_i=\alpha((1\ i))$. They are distinct transpositions because $\alpha$ is injective. For $i\ne j$, $(1\ i)(1\ j)$ has order $3$, so $t_it_j$ has order $3$. Two distinct transpositions have product of order $3$ exactly when their two-point supports intersect in one point: disjoint ones commute and their product has order $2$, whereas $(a\ b)(a\ c)$ is a $3$-cycle. Thus the supports of the $t_i$ intersect pairwise.

For $n=2$, there is only one image transposition; choose its two points as $a,b_2$. For $n=3$, the two image transpositions share a point, which can be named $a$, with their other points $b_2,b_3$.

For $n\ge4$, take two images with supports $\{a,b\}$ and $\{a,c\}$. Any further two-point support meeting both either contains $a$ or is $\{b,c\}$. If $\{b,c\}$ occurs, every support meeting all three must be one of $\{a,b\},\{a,c\},\{b,c\}$: a support using a new point misses at least one of these three. Hence a pairwise intersecting family with no common point has at most three members, forming a triangle. For $n\ge5$ our family has $n-1\ge4$ members, so a triangle is impossible.

The remaining case is $n=4$. The three original transpositions $(1\ 2),(1\ 3),(1\ 4)$ have product $(1\ 4\ 3\ 2)$ of order $4$. If their images formed a triangle on three points, their product would act on only those three points and be odd, so it would be a transposition and have order $2$; the odd elements of $S_3$ are exactly its transpositions. This contradicts order preservation of that product. Thus here too all images share a point $a$. Write them as $(a\ b_i)$. Distinctness implies the $b_i$ are distinct and none equals $a$, so together these are all $n$ points.

**(d) Identify the automorphism.** For distinct $i,j\ne1$,

$$
(i\ j)=(1\ i)(1\ j)(1\ i),
$$

so the star transpositions generate all transpositions and hence all $S_n$. Define $\tau\in S_n$ by $\tau(1)=a$, $\tau(i)=b_i$. Part (c) makes this a bijection of the $n$ points. Conjugation by $\tau$ agrees with $\alpha$ on every star generator:

$$
\tau(1\ i)\tau^{-1}=(a\ b_i)=\alpha((1\ i)).
$$

Two homomorphisms agreeing on generators agree on every word, so $\alpha(g)=\tau g\tau^{-1}$ for all $g\in S_n$. Thus every automorphism is inner; every inner automorphism is already an automorphism, proving equality.

**Technique:** invariant class sizes identify a generating family; elementary support intersections then recover a relabeling of the points. The $n=4$ triangle and the $n=6$ class-size coincidence require separate checks.

**Foundations:** @cu:algebra:midterm-2:definitions:df:automorphism-characteristic, @cu:algebra:midterm-2:theorems:th:inner-characteristic, @cu:algebra:midterm-2:theorems:th:commutator-criterion.
