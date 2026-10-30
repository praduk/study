**Definitions and results used:** @[Normalizer]mt3-normalizer; @[Nontrivial p-group center]mt3-pgroups; @[Quotient correspondence]mt3-quotient-correspondence.

Induct on $|P|$. If $Z(P)\nleq H$, an element of $Z(P)\setminus H$ normalizes $H$, giving strict containment.

Otherwise $Z(P)\le H<P$. The quotient $P/Z(P)$ is smaller than $P$, and induction gives an element $gZ(P)$ outside $H/Z(P)$ that normalizes $H/Z(P)$. Equality of the conjugate subgroups in the quotient gives $gHg^{-1}Z(P)=H$. Since $Z(P)\le H$ is central, it also lies in $gHg^{-1}$, so this equality reduces to $gHg^{-1}=H$. Thus $g\in N_P(H)\setminus H$.
