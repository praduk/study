Write $|G|=p^a m$ with $p\nmid m$. A **$p$-subgroup** has order a power of $p$; a **Sylow $p$-subgroup** has order $p^a$. Write $\Syl_p(G)$ and $n_p=|\Syl_p(G)|$.

1. Sylow subgroups exist. Every $p$-subgroup lies in one.
2. Sylow $p$-subgroups are conjugate.
3. $n_p\equiv1\pmod p$ and $n_p\mid m$; more precisely $n_p=|G:N_G(P)|$.
4. $n_p=1$ iff $P\trianglelefteq G$; then $P$ is characteristic in $G$.
5. If $P\in\Syl_p(G)$ and $K\le N_G(P)$ is a $p$-subgroup, then **$K\le P$**.

**Routine:** factor $|G|$ → list divisors of $m$ → keep those congruent to $1$ modulo $p$ → use uniqueness, action, or intersection. Do not stop at several possible Sylow numbers. In a proposed simple group of composite order, discard $n_p=1$ for every $p$.

**Counting warning:** distinct order-$p$ subgroups intersect trivially, so they contribute $n_p(p-1)$ nonidentity elements when Sylow subgroups have order $p$. Distinct larger Sylow subgroups may overlap; multiplying $n_p(|P|-1)$ without proving disjointness is invalid.

**Normal $p$-subgroups lie in every Sylow $p$-subgroup.** If $K\trianglelefteq G$ is a $p$-subgroup and $P$ is Sylow, then $KP$ is a $p$-subgroup containing $P$, hence equals $P$ and $K\le P$.
