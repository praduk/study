Eliminate the implication and push negation inward:

$$\begin{aligned}(\neg(p\to(q\land r))\lor s)&\equiv(\neg(\neg p\lor(q\land r))\lor s)\\&\equiv((p\land\neg(q\land r))\lor s)\\&\equiv((p\land(\neg q\lor\neg r))\lor s).\end{aligned}$$

The last line is NNF. Distribute the outer disjunction over the conjunction:

$$((p\land(\neg q\lor\neg r))\lor s)\equiv((p\lor s)\land((\neg q\lor\neg r)\lor s)).$$

The right side is CNF, with the three-literal clause explicitly bracketed as $(\neg q\lor\neg r)\lor s$. The rewrites use implication elimination, De Morgan's laws, double negation, and distributivity.
