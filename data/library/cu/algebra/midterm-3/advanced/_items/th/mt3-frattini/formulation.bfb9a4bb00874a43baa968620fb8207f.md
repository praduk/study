**Frattini argument:** if $N\trianglelefteq G$ is finite and $P\in\Syl_p(N)$, then $G=N N_G(P)$.

**Frattini subgroup:** $\Phi(G)$ is the intersection of all maximal subgroups; if there are none, set $\Phi(G)=G$. It is characteristic. An element is a **nongenerator** when adjoining it to any proper subgroup still gives a proper subgroup. The nongenerators are exactly $\Phi(G)$ (HW2 §6.1.24 treats arbitrary groups).

For finite $G$, if $H\Phi(G)=G$, then $H=G$: otherwise a maximal subgroup containing $H$ also contains $\Phi(G)$. In an infinite group a proper subgroup need not lie in a maximal subgroup; do not use that finite argument without justification.

For a finite $p$-group $P$,

$$
\Phi(P)=P'P^p,\qquad P/\Phi(P)\cong\F_p^r,
$$

where $P^p=\langle x^p:x\in P\rangle$. **Burnside's basis theorem:** elements form a minimal generating set of $P$ iff their cosets form a vector-space basis of $P/\Phi(P)$. Thus $r$ is the minimum number of generators and every minimal generating set has size $r$.

If $\alpha$ has order prime to $p$ and induces the identity on $P/\Phi(P)$, then $\alpha=1$. Consequently a finite group of automorphisms of order prime to $p$ embeds in $\GL_r(\F_p)$. See all six subparts of HW2 §6.1.26.

**Do not confuse** Frattini's argument (factorization), the Frattini subgroup (nongenerators), and Burnside's basis theorem (generators of finite $p$-groups).

For the arbitrary-group nongenerator proof, the only set-theoretic tool is **Zorn's lemma**: a partially ordered set in which every chain has an upper bound has a maximal element. Here the order is subgroup inclusion; the proof must verify that each chain's union remains proper. No such tool is needed for finite groups.
