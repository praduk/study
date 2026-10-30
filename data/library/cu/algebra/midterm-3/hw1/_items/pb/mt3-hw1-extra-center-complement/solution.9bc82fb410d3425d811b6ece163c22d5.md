**Definitions and results used:** @[A central semidirect factor gives a direct product]mt3-semidirect; @[Every nontrivial finite p-group has nontrivial center]mt3-pgroups; @[Center definition and subgroup element orders]mt3-foundations.

**Technique:** A central semidirect factor makes the product direct; the other p-group factor contributes an unavoidable center.

Suppose such $H$ exists. Since $Z(G)$ is central, it commutes with $H$, so this would actually be an internal direct product. Also $H\ne1$, since otherwise $G=Z(G)$ would be abelian.

The nontrivial finite $p$-group $H$ has $Z(H)\ne1$. Every element of $Z(H)$ commutes with $H$ and with $Z(G)$; because $G=HZ(G)$, it commutes with all of $G$. Therefore

$$
1\ne Z(H)\le H\cap Z(G)=1,
$$

a contradiction.
