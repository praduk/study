**(b) Transitivity of characteristicity.** Let $\alpha\in\operatorname{Aut}(G)$. Since $K$ is characteristic, $\alpha(K)=K$. The restriction $\alpha|_K$ is an automorphism of $K$: it preserves multiplication, is injective, and maps $K$ onto $K$. Since $H$ is characteristic in $K$, $\alpha|_K(H)=H$. Thus $\alpha(H)=H$ for every automorphism of $G$, proving $H$ characteristic in $G$.

**Apply this to S₄.** Let

$$
V=\{1,(1\ 2)(3\ 4),(1\ 3)(2\ 4),(1\ 4)(2\ 3)\}.
$$

First we verify $A_4$ is characteristic in $S_4$ using its commutator description. Because $S_4/A_4\cong C_2$ is abelian, $S_4'\le A_4$. For the involutions $a=(1\ 2)$, $b=(2\ 3)$, the commutator is $[a,b]=abab=(ab)^2=(1\ 3\ 2)$, a $3$-cycle. Normality of $S_4'$ then puts every conjugate $3$-cycle in $S_4'$. The $3$-cycles generate $A_4$: any even permutation is a product of pairs of transpositions, and each pair is either identity, a $3$-cycle when the transpositions share one point, or, for disjoint transpositions,

$$
(a\ b)(c\ d)=(a\ c\ b)(a\ c\ d).
$$

Therefore $S_4'=A_4$. Every automorphism sends commutators to commutators and hence preserves the subgroup they generate, so $A_4$ is characteristic in $S_4$.

Next $V$ is characteristic in $A_4$: the elements of order $2$ in $A_4$ are exactly the three double transpositions, so $V$ is the identity together with all order-$2$ elements. Automorphisms preserve orders, hence preserve $V$. The transitivity just proved gives $V$ characteristic in $S_4$.

**(c) Counterexample.** Take $G=A_4$, $K=V$, and $H=\langle(1\ 2)(3\ 4)\rangle$. We just proved $K$ characteristic in $A_4$. Since $K$ is abelian, every subgroup of $K$, including $H$, is normal in $K$. But conjugation by $g=(1\ 2\ 3)$ sends the generator of $H$ to

$$
g(1\ 2)(3\ 4)g^{-1}=(2\ 3)(1\ 4),
$$

which is not in $H$. Hence $H$ is not normal in $G$.

**Technique:** restricting an arbitrary automorphism proves characteristicity. Restricting only conjugations proves normality; these two statements are not interchangeable.

**Foundations:** @cu:algebra:midterm-2:definitions:df:automorphism-characteristic, @cu:algebra:midterm-2:theorems:th:inner-characteristic, @cu:algebra:midterm-2:theorems:th:commutator-criterion.
