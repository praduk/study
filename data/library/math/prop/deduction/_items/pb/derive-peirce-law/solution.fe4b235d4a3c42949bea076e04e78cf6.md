1. Assume $H=(A\to B)\to A$.
2. For RAA, assume $\neg A$.
3. To obtain $A\to B$, assume $A$.
4. From $A$ and $\neg A$, infer $\false$ by $\neg E$.
5. From $\false$, infer $B$ by $\false E$.
6. Close lines 3–5 by $\to I$ to obtain $A\to B$.
7. From $H$ and $A\to B$, infer $A$ by $\to E$.
8. From $A$ and $\neg A$, infer $\false$.
9. Close the RAA subproof to infer $A$, discharging $\neg A$.
10. Close the outer subproof by $\to I$ to infer $((A\to B)\to A)\to A$.

All assumptions are discharged, so the result is a theorem.
