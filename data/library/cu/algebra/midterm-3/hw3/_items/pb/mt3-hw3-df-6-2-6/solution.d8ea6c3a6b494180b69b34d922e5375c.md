**Definitions and results used:** @[Sylow numbers and the normalizer index formula]mt3-sylow; @[Faithful actions of simple groups and prime powers in factorials]mt3-actions; @[Normalizers and subgroup-order divisibility]mt3-foundations.

**Technique:** Convert a small Sylow number to a faithful permutation representation; compare prime powers in the factorial.

If a simple group $G$ acts nontrivially on its $n_p>1$ Sylow $p$-subgroups, the action is faithful. Hence $|G|\mid n_p!$.

- $2205=3^2\cdot5\cdot7^2$: Sylow allows $n_3=7$ or $49$. If $n_3=7$, then $2205\nmid7!$ because $7^2\nmid7!$. If $n_3=49$, choose $P\in\Syl_3(G)$; its normalizer has order $45$. Inside this normalizer, the Sylow $5$-subgroup $Q$ is unique because its number divides $9$ and is $1\pmod5$. Thus $N_G(P)\le N_G(Q)$, so $n_5=[G:N_G(Q)]$ divides $49$. The only divisor of $49$ congruent to $1\pmod5$ is $1$, again a contradiction.
- $4125=3\cdot5^3\cdot11$: $n_5=11$, but $5^3\nmid11!$.
- $5103=3^6\cdot7$: $n_3=7$, but $3^6\nmid7!$.
- $6545=5\cdot7\cdot11\cdot17$: $n_5=11$, but $17\nmid11!$.
- $6435=3^2\cdot5\cdot11\cdot13$: $n_5=11$, but $13\nmid11!$.

Each contradiction rules out simplicity, not merely normality of a particular Sylow subgroup.
