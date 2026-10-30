**Definitions and results used:** @[Sylow theorem]cu:algebra:midterm-3:sylow:th:mt3-sylow; @[Unique, normal, and characteristic Sylow subgroups]cu:algebra:midterm-3:sylow:th:mt3-sylow-normality; @[Normalizer]cu:algebra:midterm-3:foundations:df:mt3-normalizer; @[Lagrange’s theorem and the index formula]cu:algebra:midterm-3:foundations:th:mt3-lagrange.

**Technique:** A Sylow subgroup unique in one normalizer forces inclusion in another normalizer; compare their orders.

Assume simplicity throughout, so no Sylow number is $1$. Use this observation repeatedly: if $Q$ is the unique Sylow subgroup for its prime inside $N_G(P)$, then $N_G(P)\le N_G(Q)$.

- $4095=3^2\cdot5\cdot7\cdot13$: Sylow gives $n_7=15$, $n_{13}=105$. For $P\in\Syl_7(G)$, $|N_G(P)|=273=3\cdot7\cdot13$. In this group the Sylow $13$-number divides $21$ and is $1\pmod{13}$, hence is $1$. Thus $273$ must divide $|N_G(Q)|=4095/105=39$, impossible.
- $4389=3\cdot7\cdot11\cdot19$: $n_7=57$, $n_{11}=133$. The normalizer of a Sylow $7$-subgroup has order $77$. Its Sylow $11$-subgroup is unique, forcing $77\mid|N_G(Q)|=4389/133=33$, impossible.
- $5313=3\cdot7\cdot11\cdot23$: $n_{11}=23$, $n_7=253$. A Sylow $11$-normalizer has order $231$. Its Sylow $7$-number divides $33$ and is $1\pmod7$, hence is $1$. This forces $231\mid5313/253=21$, impossible.
- $6669=3^3\cdot13\cdot19$: $n_{13}=27$, $n_{19}=39$. A Sylow $13$-normalizer has order $247=13\cdot19$. Its Sylow $19$-subgroup is unique, forcing $247\mid6669/39=171$, impossible.
