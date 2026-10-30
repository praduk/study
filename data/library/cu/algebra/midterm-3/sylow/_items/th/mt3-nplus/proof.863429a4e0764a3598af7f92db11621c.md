**Definitions and results used:** @[Conjugation orbits and orbit-stabilizer]mt3-actions; @[The Sylow normalizer lemma]mt3-sylow.

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
