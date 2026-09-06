For identity, open a subproof with assumption $A$, reiterate $A$, and close it by $\to I$ to obtain $A\to A$.

For double-negation elimination, take premise $\neg\neg A$. Open a subproof with assumption $\neg A$. The premise and assumption yield $\false$ by $\neg E$. Close by RAA to infer $A$.

For excluded middle, assume $\neg(A\lor\neg A)$. Inside that subproof, assume $A$; infer $A\lor\neg A$ by $\lor I$, contradict the outer assumption, and close the inner subproof by $\neg I$ to get $\neg A$. Infer $A\lor\neg A$ from this by $\lor I$, again contradicting the outer assumption. RAA discharges $\neg(A\lor\neg A)$ and yields $A\lor\neg A$ with no premises.

For modus tollens, take $A\to B$ and $\neg B$ as premises. Assume $A$. Modus ponens $\to E$ gives $B$, which with $\neg B$ gives $\false$. Close the subproof by $\neg I$ to conclude $\neg A$. Every temporary assumption has been explicitly discharged.
