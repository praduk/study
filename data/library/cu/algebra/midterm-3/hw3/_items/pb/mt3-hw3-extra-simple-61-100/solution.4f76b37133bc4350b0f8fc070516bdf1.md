**Definitions and results used:** @[Sylow theorem]cu:algebra:midterm-3:sylow:th:mt3-sylow; @[Unique, normal, and characteristic Sylow subgroups]cu:algebra:midterm-3:sylow:th:mt3-sylow-normality; @[Counting distinct prime-order subgroups]cu:algebra:midterm-3:sylow:th:mt3-prime-order-intersections; @[Faithful actions of simple groups and the alternating-group obstruction]cu:algebra:midterm-3:foundations:th:mt3-simple-actions; @[Every index-two subgroup is normal]cu:algebra:midterm-3:foundations:th:mt3-index-two; @[A nontrivial finite p-group has nontrivial center]cu:algebra:midterm-3:sylow:th:mt3-pgroups; @[Groups of order p² are abelian]cu:algebra:midterm-3:sylow:th:mt3-p-square-abelian; @[Abelian simple groups have prime order]cu:algebra:midterm-3:foundations:th:mt3-abelian-simple; @[Normalizer]cu:algebra:midterm-3:foundations:df:mt3-normalizer; @[Lagrange’s theorem and the index formula]cu:algebra:midterm-3:foundations:th:mt3-lagrange.

**Technique:** Exhaust the interval by normal Sylow subgroups, then treat the four exceptions with actions, counting, and a Sylow-intersection normalizer.

Prime-order groups are cyclic. The prime powers in this interval that are not prime are $64$ and $81$; a nontrivial finite $p$-group has nontrivial center, so it is simple only when its order is prime.

For the following composite orders, the Sylow subgroup for the displayed prime is unique: factor the order, then check that $1$ is the only divisor of its prime-to-$p$ part congruent to $1\pmod p$.

$$
\begin{aligned}
(|G|,p)={}&(62,31),(63,7),(65,13),(66,11),(68,17),(69,23),\\
&(70,7),(74,37),(75,5),(76,19),(77,11),(78,13),\\
&(82,41),(84,7),(85,17),(86,43),(87,29),(88,11),\\
&(91,13),(92,23),(93,31),(94,47),(95,19),(98,7),\\
&(99,11),(100,5).
\end{aligned}
$$

Every such group therefore has a nontrivial proper normal subgroup. The only remaining composite orders are $72,80,90,96$.

- **$72=2^3\cdot3^2$:** $n_3=1$ or $4$. Under simplicity, $n_3=4$, so the conjugation action embeds $G$ in $S_4$, impossible since $72\nmid24$.
- **$80=2^4\cdot5$:** simplicity forces $n_5=16$. The $64$ elements of order $5$ leave exactly $16$ elements, forcing a unique Sylow $2$-subgroup.
- **$96=2^5\cdot3$:** $n_2=1$ or $3$. Under simplicity the action on the three Sylow $2$-subgroups embeds $G$ in $S_3$, impossible.
- **$90=2\cdot3^2\cdot5$:** simplicity forces $n_3=10$ and $n_5=6$. If all Sylow $3$-subgroups intersect trivially in pairs, they contribute $10(9-1)=80$ nonidentity elements; the Sylow $5$-subgroups contribute another $6(5-1)=24$, impossible. Hence two distinct Sylow $3$-subgroups $P,R$ intersect in a subgroup $D$ of order $3$. Since groups of order $9$ are abelian, both $P$ and $R$ lie in $N_G(D)$. This normalizer has at least two Sylow $3$-subgroups, so their number is at least $4$. Its order is $9k$ with $k\mid10$; therefore $k\ge4$, leaving orders $45$ or $90$. Order $90$ makes $D$ normal in $G$; order $45$ makes its normalizer an index-$2$ normal subgroup. Either contradicts simplicity.

The list exhausts all composite integers in the interval. Thus the only simple groups in the stated range have prime order and are abelian. No odd-order or two-prime solvability theorem was used.
