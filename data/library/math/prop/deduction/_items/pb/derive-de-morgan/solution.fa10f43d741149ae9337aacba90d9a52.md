For the first direction, take $\neg A\lor\neg B$ as premise and assume $A\land B$. Apply $\lor E$ to the premise. In the $\neg A$ case, $\land E$ gives $A$ and hence $\false$; in the $\neg B$ case, $\land E$ gives $B$ and hence $\false$. Thus the assumption $A\land B$ leads to $\false$, and $\neg I$ gives $\neg(A\land B)$.

For the reverse direction, take $\neg(A\land B)$ as premise and use the derived theorem $A\lor\neg A$. Apply $\lor E$. In the $\neg A$ case, infer $\neg A\lor\neg B$ immediately. In the $A$ case, assume $B$; then $A\land B$ contradicts the premise, so $\neg I$ yields $\neg B$, and $\lor I$ yields $\neg A\lor\neg B$. The case split gives the desired disjunction.

The second derivation uses excluded middle, which was obtained from RAA; that is its classical step.
