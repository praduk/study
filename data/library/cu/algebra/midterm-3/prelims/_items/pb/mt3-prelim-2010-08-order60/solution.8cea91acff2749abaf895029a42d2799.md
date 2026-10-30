**Technique trigger:** for an isomorphism conclusion, search for a faithful action of the right degree. Here a degree-$5$ action places a group of order $60$ inside $A_5$, which also has order $60$.

**Definitions and results used:** @[Simple groups]cu:algebra:midterm-3:foundations:df:mt3-simple and @[abelian simple groups have prime order]cu:algebra:midterm-3:foundations:th:mt3-abelian-simple; @[Faithful simple-group actions into alternating groups]cu:algebra:midterm-3:foundations:th:mt3-simple-actions; @[Sylow's theorem]cu:algebra:midterm-3:sylow:th:mt3-sylow, @[unique Sylow subgroups are normal]cu:algebra:midterm-3:sylow:th:mt3-sylow-normality, and @[the Sylow (N)+ corollary]cu:algebra:midterm-3:sylow:th:mt3-intersection; @[Index-two normality]cu:algebra:midterm-3:foundations:th:mt3-index-two, @[normalizers]cu:algebra:midterm-3:foundations:df:mt3-normalizer, and @[Lagrange's theorem]cu:algebra:midterm-3:foundations:th:mt3-lagrange.

Since $60$ is composite, the simple group $G$ is nonabelian. A Sylow $2$-subgroup has order $4$, and

$$
n_2\mid15,\qquad n_2\equiv1\pmod2,
$$

so $n_2\in\{1,3,5,15\}$.

The value $1$ contradicts simplicity. The value $3$ would give a faithful conjugation action on three Sylow subgroups, embedding $G$ in $A_3$, impossible by orders.

If $n_2=5$, that action embeds $G$ in $A_5$. Since $|G|=60=|A_5|$, the image is all of $A_5$, giving $G\cong A_5$.

It remains to treat $n_2=15$. Since $15\not\equiv1\pmod4$, the corollary gives distinct $P,Q\in\Syl_2(G)$ with $D=P\cap Q$ of index $2$ in each. Thus $|D|=2$, and index-two normality gives

$$
P,Q\le N_G(D).
$$

This normalizer strictly contains $P$. Its order is therefore a multiple of $4$ greater than $4$ dividing $60$, hence one of $12,20,60$.

- Order $60$ would make $D$ a proper nontrivial normal subgroup of $G$, impossible.
- Order $20$ would give a subgroup of index $3$, hence an impossible faithful coset action into $A_3$.
- Order $12$ gives a subgroup of index $5$. The coset action embeds $G$ in $A_5$, and equal orders again give $G\cong A_5$.

Thus every possible case either contradicts simplicity or identifies $G$ with $A_5$.

**What changed from the order-$120$ problem?** An order-$12$ normalizer now has index $5$, and the resulting inclusion in $A_5$ has equal orders. It proves an isomorphism rather than a contradiction. This argument does not need the separate theorem that $A_5$ or $A_6$ is simple.
