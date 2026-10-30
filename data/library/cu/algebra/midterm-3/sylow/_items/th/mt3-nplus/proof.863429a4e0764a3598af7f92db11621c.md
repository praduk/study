**Definitions and results used:** @[Group action, orbit, and stabilizer]cu:algebra:midterm-3:foundations:df:mt3-group-action; @[Orbit–stabilizer theorem]cu:algebra:midterm-3:foundations:th:mt3-actions; @[Sylow normalizer lemma]cu:algebra:midterm-3:sylow:th:mt3-sylow-normalizer; @[Lagrange’s theorem and the index formula]cu:algebra:midterm-3:foundations:th:mt3-lagrange.

Fix $P\in\Syl_p(G)$ and let it act on $\Syl_p(G)$ by conjugation. For each $Q$, its stabilizer is $N_P(Q)=P\cap N_G(Q)$.

This stabilizer is a $p$-subgroup of $N_G(Q)$, so the normalizer lemma gives $N_P(Q)\le Q$. Thus $N_P(Q)\le P\cap Q$. Conversely every element of $P\cap Q$ normalizes $Q$, so

$$
N_P(Q)=P\cap Q.
$$

Therefore the orbit containing $Q$ has size $[P:P\cap Q]$. The only singleton orbit is $\{P\}$. Choose **one representative from each other orbit**; summing their orbit sizes yields

$$
n_p=1+\sum_{\text{nontrivial orbit representatives }Q}[P:P\cap Q]\equiv1\pmod{p^k}.
$$

The sum is over orbit representatives, not all Sylow subgroups; summing over all of them would double-count.
