**Definitions and results used:** @[Wreath products as factor-permuting semidirect products]mt3-semidirect; @[Left regular action, disjoint p-cycles, and prime exponent in a factorial]mt3-actions; @[A Sylow subgroup has the full prime-power part of the group order]mt3-sylow; @[Internal semidirect recognition and nontrivial actions]mt3-semidirect.

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
