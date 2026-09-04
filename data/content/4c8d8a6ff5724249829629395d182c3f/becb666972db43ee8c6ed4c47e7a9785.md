A **binary relation from $A$ to $B$** is a subset $R\subseteq A\times B$. Write $aRb$ for $\langle a,b\rangle\in R$. Its domain and range are

$$
\operatorname{dom}(R)=\{a:\exists b\,aRb\},\qquad
\operatorname{ran}(R)=\{b:\exists a\,aRb\}.
$$

The inverse relation is $R^{-1}=\{\langle b,a\rangle:aRb\}$. If $R\subseteq A\times B$ and $S\subseteq B\times C$, then

$$
S\circ R=\{\langle a,c\rangle:\exists b\,(aRb\land bSc)\}.
$$

For a relation on $A$, the identity relation is
$\mathrm{id}_A=\{\langle a,a\rangle:a\in A\}$. Relations are sets, so all these constructions must ultimately be justified by Separation and Replacement from set-sized domains.
