**Definitions and results used:** @[Frattini argument inside the normalizer of PN]mt3-frattini-argument; @[normalizers, centralizers, subgroup correspondence, and coprime intersections]mt3-foundations; @[recognizing P as a Sylow subgroup of PN]mt3-sylow.

**Technique:** Apply Frattini to PN inside its normalizer; then a commutator lies in both P and N.

**(a)** Set $K=N_G(PN)$. The full inverse image of $N_{\overline G}(\overline P)$ is $K$, since $\overline P=PN/N$. Also $PN\nsubg K$ and $P\in\Syl_p(PN)$: indeed $P\cap N=1$, so $|PN|=|P||N|$. Frattini's argument inside $K$ yields

$$
K=(PN)N_K(P)=N N_G(P).
$$

Here $N_G(P)\le K$ because it normalizes both $P$ and $N$, and $P\le N_G(P)$. Taking images gives (a).

**(b)** The image of a centralizer is certainly contained in the centralizer of the image. For the reverse containment, let $\overline x\in C_{\overline G}(\overline P)$. By (a), choose $x\in N_G(P)$ representing this coset. For each $u\in P$, centralization modulo $N$ gives $xux^{-1}u^{-1}\in N$, while normalization gives this element in $P$. Since $P\cap N=1$, it is $1$. Thus $x\in C_G(P)$.

**Trap:** normalizers and centralizers do not in general commute with arbitrary quotients; the coprimality assumption is doing real work.
