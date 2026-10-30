Use the lecture commutator $[x,y]=xyx^{-1}y^{-1}$, and $[H,K]=\langle[h,k]:h\in H,k\in K\rangle$. Dummit–Foote uses $x^{-1}y^{-1}xy$; these conventions generate the same commutator subgroups. Never mix element-level formulas without checking the convention.

**Upper central series:** $Z_0(G)=1$, and

$$
Z_{i+1}(G)/Z_i(G)=Z(G/Z_i(G)).
$$

Equivalently $Z_{i+1}(G)=\{x:[x,G]\subseteq Z_i(G)\}$. This is the **preimage** of a quotient center, not a subgroup written only inside the quotient.

**Lower central series:** use the lecture indexing $L_0(G)=G$, $L_{i+1}(G)=[G,L_i(G)]$. Dummit–Foote denotes these terms $G^i$. Another common convention is $\gamma_1(G)=G$, so $L_i=\gamma_{i+1}$.

**Derived series:** $G^{(0)}=G$, $G^{(i+1)}=[G^{(i)},G^{(i)}]$. The first terms agree, $L_1=G'$, but later terms generally do not.

A group is **nilpotent of class $c$** if $c$ is the smallest nonnegative integer with $Z_c(G)=G$, equivalently $L_c(G)=1$. The trivial group has class0; nontrivial abelian groups have class1. A group is **solvable of derived length $d$** if $d$ is the smallest nonnegative integer with $G^{(d)}=1$.

All three series have characteristic terms. Homomorphisms send commutators to commutators. Therefore $H\le G$ gives $L_i(H)\le L_i(G)$ and $H^{(i)}\le G^{(i)}$; a surjection maps lower/derived terms onto the corresponding terms of the image. Upper centers do not obey the analogous subgroup equality.

**Diagnostic example $S_3$.** $Z_i(S_3)=1$ for every $i$; $L_1=A_3$ and $L_i=A_3$ for all $i\ge1$; but $S_3'=A_3$ and $S_3''=1$. Indeed a transposition conjugates a 3-cycle to its inverse, so their commutator is a nonidentity 3-cycle. Thus $S_3$ is solvable of length2 and not nilpotent.

**Computation pattern:** find $G'$ using relations; repeat with the whole group for $L_i$, with the current term for $G^{(i)}$; compute centers of successive quotients for $Z_i$.
