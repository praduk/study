For $A\subseteq G$,

$$
\begin{aligned}
C_G(A)&=\{g\in G:ga=ag\text{ for every }a\in A\},\\
Z(G)&=C_G(G),\\
N_G(A)&=\{g\in G:gAg^{-1}=A\}.
\end{aligned}
$$

Write $C_G(a)$ for $C_G(\{a\})$. Under conjugation, these are respectively a pointwise stabilizer, the action kernel, and a setwise stabilizer. All are subgroups, and $C_G(A)\le N_G(A)$.
A subgroup $H\le G$ is **normal**, written $H\trianglelefteq G$, exactly when $N_G(H)=G$, equivalently $gHg^{-1}=H$ for every $g\in G$.
Normalizer means equality of sets; it does not require $ghg^{-1}=h$ for every $h$. That stronger condition defines the centralizer. $Z(G)$ is abelian, but centralizers need not be.
