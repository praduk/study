**Step 1: normality.** Conjugation by $v$ fixes $v^4$. Conjugation by $u$ gives $uv^4u=(v^5)^4=v^{20}=v^4$. The generators $u,v$ thus centralize $v^4$, so $\langle v^4\rangle\le Z(M)$ and is normal.

**Step 2: lift the quotient vertices.** Write $L=\langle v^4\rangle$. It has order $2$, so the quotient has order $8$. By the lattice correspondence, its subgroups are exactly $T/L$ for subgroups $T\le M$ containing $L$. From the complete lattice in 2.5.14 these are:

- $L$ itself, giving the identity vertex;
- $\langle u,v^4\rangle,\langle v^2\rangle,\langle uv^2\rangle$, giving three order-$2$ vertices;
- $\langle u,v^2\rangle,\langle v\rangle,\langle uv\rangle$, giving three order-$4$ vertices;
- $M$, giving the top vertex.

Let bars denote cosets modulo $L$. The order-$4$ vertices are $\langle\bar u,\bar v^2\rangle$, $\langle\bar v\rangle$, $\langle\bar u\bar v\rangle$. The first covers all three order-$2$ vertices $\langle\bar u\rangle,\langle\bar v^2\rangle,\langle\bar u\bar v^2\rangle$; each of the other two covers only $\langle\bar v^2\rangle$. All order-$2$ vertices cover $1$, and the whole quotient covers the three order-$4$ vertices. The diagram below is exactly the lattice of $C_2\times C_4$.

**Step 3: establish the group type, not just the lattice.** In the quotient $\bar v^4=1$, and the defining relation becomes $\bar v\bar u=\bar u\bar v^5=\bar u\bar v$. Thus the two quotient generators commute. Also $\bar u^2=1$. Define

$$
f:C_2\times C_4\longrightarrow M/L,\qquad f(i,j)=\bar u^i\bar v^j.
$$

The order relations make this well defined, and commutativity makes it a homomorphism. It is surjective because $\bar u,\bar v$ generate the quotient. Domain and codomain both have order $8$, so it is bijective. Hence $M/L\cong C_2\times C_4$.

![Complete subgroup lattice for 3.3.6 — Quotient lattice of the modular group](/media/b5055cd981d56a32e86a7a6d65bcdc22f4ff6377263a0844196cf97d431d2395.png#width=100&invert=lightness)

**Technique:** correspondence gives the lattice; a surjective map plus a cardinality check determines the actual group.

**Foundations:** @cu:algebra:midterm-2:theorems:th:first-isomorphism, @cu:algebra:midterm-2:theorems:th:second-isomorphism, @cu:algebra:midterm-2:theorems:th:correspondence, @cu:algebra:midterm-2:theorems:th:product-order.
