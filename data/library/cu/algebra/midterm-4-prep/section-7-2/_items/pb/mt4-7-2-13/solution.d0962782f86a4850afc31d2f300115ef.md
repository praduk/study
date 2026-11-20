**Strategy.** Test centrality by conjugating with group elements. Conjugation permutes the members of a conjugacy class, so its sum is fixed. Conversely, if a group-ring element is fixed, compare coefficients to see what must agree.

**(a) Show that each class sum is central.** Fix $g\in G$ and a @[conjugacy class]cu:algebra:week-5:df:conjugacy-classes $K$. If $h=utu^{-1}$ is conjugate to $t$, then $ghg^{-1}=(gu)t(gu)^{-1}$ is still conjugate to $t$. Conjugating by $g^{-1}$ gives the inverse operation, so conjugation by $g$ permutes $K$. Thus

$$
g s_K g^{-1}=\sum_{h\in K}ghg^{-1}=\sum_{h\in K}h=s_K.
$$

It follows that $g s_K=s_K g$ for every $g\in G$. Scalars from $R$ are central in the @[group ring]mt4-group-ring. By distributing over an arbitrary sum $\sum_{g\in G}a_g g$, we see that $s_K$ commutes with every element of $RG$. This puts $s_K$ in the @[center]mt4-ring-center.

**(b) From class sums to the center.** Every $R$-linear combination of the $s_K$ is central. Indeed, each scalar coefficient and each class sum commutes with every element of $RG$, and addition preserves that property.

**(b) From the center to class sums.** Write $z=\sum_{h\in G}a_h h$ and suppose $z$ is central. For each $g\in G$, $z=gzg^{-1}$. On the right, the coefficient of $t\in G$ comes from the unique $h$ with $ghg^{-1}=t$, namely $h=g^{-1}tg$. Comparing the two coefficients gives $a_t=a_{g^{-1}tg}$.

Thus the coefficients of $z$ are constant on each conjugacy class. Conjugacy is an equivalence relation (identity, inverse, and product of conjugating elements give its three properties), so the classes @[partition the group]math:set:relations-functions:th:equivalence-partition. Grouping the terms of $z$ gives $z=\sum_K a_Ks_K$, where $a_K$ is the common coefficient on $K$. This proves the other inclusion.
