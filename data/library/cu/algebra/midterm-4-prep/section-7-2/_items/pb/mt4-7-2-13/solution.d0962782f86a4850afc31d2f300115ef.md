**Strategy.** Test centrality by conjugating with group elements. Conjugation permutes the members of a conjugacy class, so its sum is fixed. Conversely, if a group-ring element is fixed, compare coefficients to see what must agree.

**(a) Show that each class sum is central.** Fix $g\in G$ and a @[conjugacy class]cu:algebra:week-5:df:conjugacy-classes $\mathcal K$. Write $K=\sum_{h\in\mathcal K}h$ for its class sum. If $h=utu^{-1}$ is conjugate to $t$, then $ghg^{-1}=(gu)t(gu)^{-1}$ is still conjugate to $t$. Conjugating by $g^{-1}$ gives the inverse operation, so conjugation by $g$ permutes $\mathcal K$. Thus

$$
gKg^{-1}=\sum_{h\in\mathcal K}ghg^{-1}=\sum_{h\in\mathcal K}h=K.
$$

It follows that $gK=Kg$ for every $g\in G$. Scalars from $R$ are central in the @[group ring]mt4-group-ring. By distributing over an arbitrary sum $\sum_{g\in G}a_g g$, we see that $K$ commutes with every element of $RG$. This puts $K$ in the @[center]mt4-ring-center.

**(b) From class sums to the center.** Every $R$-linear combination of the class sums is central. Indeed, each scalar coefficient and each class sum commutes with every element of $RG$, and addition preserves that property.

**(b) From the center to class sums.** Write $\alpha=\sum_{h\in G}a_h h$ and suppose $\alpha$ is central. For each $g\in G$, $\alpha=g\alpha g^{-1}$. On the right, the coefficient of $t\in G$ comes from the unique $h$ with $ghg^{-1}=t$, namely $h=g^{-1}tg$. Comparing the two coefficients gives $a_t=a_{g^{-1}tg}$.

Thus the coefficients of $\alpha$ are constant on each conjugacy class. Conjugacy is an equivalence relation (identity, inverse, and product of conjugating elements give its three properties), so the classes @[partition the group]math:set:relations-functions:th:equivalence-partition. Grouping the terms of $\alpha$ gives $\alpha=\sum_{\mathcal K}a_{\mathcal K}K$, where $a_{\mathcal K}$ is the common coefficient on the class $\mathcal K$. This proves the other inclusion.
