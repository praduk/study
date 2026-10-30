**Definitions and results used:** @[Permutation and regular wreath products]cu:algebra:midterm-3:semidirect:df:mt3-wreath-product; @[Regular action]cu:algebra:midterm-3:foundations:df:mt3-regular-action; @[Cycle structure of a prime-order permutation]cu:algebra:midterm-3:foundations:th:mt3-prime-order-cycles; @[The exponent of a prime in a factorial]cu:algebra:midterm-3:foundations:th:mt3-factorial-valuation; @[Sylow p-subgroup]cu:algebra:midterm-3:sylow:df:mt3-sylow-subgroup; @[Semidirect product construction and internal recognition]cu:algebra:midterm-3:semidirect:th:mt3-semidirect-recognition.

**Technique:** Build disjoint cycles inside blocks, then a cycle of blocks; compare the resulting order with the p-part of the factorial.

**(a)** The regular action has degree $|K|$. Hence the base group is $L^{|K|}$ and

$$
|L\wr K|=|L|^{|K|}|K|.
$$

**(b)** Here the base is $C_p^p$, and the outer $C_p$ cyclically permutes its $p$ factors, giving order $p^p p=p^{p+1}$. This action is nontrivial, so the product is nonabelian: a nonidentity element supported on one coordinate does not commute with the cyclic shift.

For an explicit embedding, use the $p^2$ points $(i,j)\in\F_p^2$. For each $i$, let $a_i$ add $1$ to the second coordinate in block $\{i\}\times\F_p$ and fix all other blocks. Let $b(i,j)=(i+1,j)$. The disjoint $p$-cycles $a_i$ generate $C_p^p$, and $b a_i b^{-1}=a_{i+1}$. The block shift $b$ has order $p$ and its subgroup intersects the base trivially. Thus these permutations realize precisely $C_p^p\semid C_p$.

Finally the exponent of $p$ dividing $(p^2)!$ is

$$
\left\lfloor\frac{p^2}{p}\right\rfloor+\left\lfloor\frac{p^2}{p^2}\right\rfloor=p+1.
$$

The embedded subgroup therefore has the full $p$-part of $|S_{p^2}|$ and is Sylow.
