Prove the stronger invariant by induction on a derivation: any valuation satisfying every undischarged assumption at a line satisfies that line's formula. Premises, open assumptions, and reiterations satisfy the invariant immediately, and $\true I$ is valid because every valuation satisfies $\true$.

For $\land I$ and $\land E$, the invariant follows from the truth condition for conjunction. For $\lor I$, a true disjunct makes the disjunction true. For $\lor E$, if a valuation satisfies $A\lor B$, it satisfies at least one disjunct. In the corresponding subderivation, the induction hypothesis with that disjunct added to the open assumptions gives $C$. Both cases yield the same $C$.

For $\to E$, truth of $A\to B$ and $A$ forces truth of $B$. For $\to I$, consider a valuation satisfying the remaining open assumptions. If it falsifies $A$, it satisfies $A\to B$ automatically. If it satisfies $A$, the induction hypothesis applied to the subderivation gives $B$, so it again satisfies $A\to B$.

For $\neg E$, no valuation can satisfy both $A$ and $\neg A$, so the inferred $\false$ is reached under no valuation satisfying all current assumptions. For $\neg I$, if a valuation satisfying the remaining assumptions also satisfied $A$, the induction hypothesis would make it satisfy $\false$, impossible; hence it satisfies $\neg A$. For $\false E$, there is no valuation satisfying the premise $\false$, so the preservation condition holds vacuously.

For $\leftrightarrow I$, the two true conditionals give equal truth values to $A$ and $B$, so the biconditional is true. Each $\leftrightarrow E$ conclusion is true whenever the biconditional is true. Finally, for RAA, suppose a valuation satisfies the remaining assumptions. If it falsified $A$, it would satisfy $\neg A$; the induction hypothesis on the subderivation would then make it satisfy $\false$, impossible. It must satisfy $A$.

All rules preserve the invariant. At the last line of a derivation from $\Gamma$, every valuation satisfying $\Gamma$ therefore satisfies $A$. Thus $\Gamma\models A$.
