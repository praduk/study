**Definitions and results used:** @[Presentation of S_n by adjacent transpositions]cu:algebra:midterm-3:advanced:th:mt3-symmetric-presentation; @[Group presentation and defining relations]cu:algebra:midterm-3:advanced:df:mt3-presentations; @[Universal mapping property of free and presented groups]cu:algebra:midterm-3:advanced:th:mt3-free-maps; @[Simplicity of alternating groups]cu:algebra:midterm-3:foundations:th:mt3-alternating-simple; @[The symmetric group has trivial center]cu:algebra:midterm-3:foundations:th:mt3-symmetric-center; @[Sign is a homomorphism]cu:algebra:midterm-3:foundations:th:mt3-sign-homomorphism; @[Homomorphism, kernel, and image]cu:algebra:midterm-3:foundations:df:mt3-homomorphism; @[Automorphisms of a finite cyclic group]cu:algebra:midterm-3:foundations:th:mt3-cyclic-automorphisms.

**Technique:** Verify presentation relations, obtain a homomorphism, then separately prove it is bijective; preserve the distinction between a homomorphism and an automorphism.

Each $t'_i$ is a product of three disjoint transpositions, so its square is $1$. Composing right to left, the adjacent products are

$$
\begin{aligned}
t'_1t'_2&=(135)(264),&t'_2t'_3&=(162)(345),\\
t'_3t'_4&=(146)(235),&t'_4t'_5&=(153)(264).
\end{aligned}
$$

Their cubes are $1$. For the six nonadjacent pairs, the products are respectively

$$
\begin{aligned}
t'_1t'_3&=(14)(23),&t'_1t'_4&=(35)(46),&t'_1t'_5&=(13)(24),\\
t'_2t'_4&=(15)(24),&t'_2t'_5&=(26)(35),&t'_3t'_5&=(12)(34).
\end{aligned}
$$

Their squares are $1$. Thus the defining Coxeter relations of $S_6$ hold, so the assignment gives a homomorphism $\varphi:S_6\to S_6$.

To check injectivity, $\ker\varphi\cap A_6$ is normal in the simple group $A_6$. It cannot be all of $A_6$, since the $3$-cycle $(12)(23)$ has nonidentity image $t'_1t'_2$. Thus $\ker\varphi\cap A_6=1$. The sign map is then injective on $\ker\varphi$, so this kernel has order at most $2$. A normal subgroup of order $2$ is central, while $Z(S_6)=1$; hence the kernel is trivial.

An injective self-map of the finite group $S_6$ is surjective. Therefore $\varphi$ is an automorphism and its five displayed images generate $S_6$. It is not inner: conjugation preserves cycle type, but $\varphi$ sends a transposition to a product of three disjoint transpositions.
