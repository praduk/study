A **derivation** is a finite, linearly displayed tree of formulas. A line may depend only on premises and on assumptions in subproofs that are still open at that line. Closing a subproof discharges the indicated assumption; its internal lines are then unavailable except through the rule that closed it. Reiteration permits an available earlier formula to be copied.

The calculus has these rules:

- **Premise:** a member of the premise set may be entered.
- **Assumption:** begin a subproof with any formula $A$.
- **Reiteration:** from available $A$, infer $A$.
- **$\true I$:** infer $\true$ with no premises.
- **$\land I$:** from $A$ and $B$, infer $A\land B$.
- **$\land E$:** from $A\land B$, infer either $A$ or $B$.
- **$\lor I$:** from $A$, infer $A\lor B$; from $B$, infer $A\lor B$.
- **$\lor E$:** from $A\lor B$, a subproof from assumption $A$ to $C$, and a subproof from assumption $B$ to the same $C$, infer $C$, discharging both assumptions.
- **$\to I$:** from a subproof beginning with assumption $A$ and ending with $B$, infer $A\to B$, discharging $A$.
- **$\to E$:** from $A\to B$ and $A$, infer $B$.
- **$\neg I$:** from a subproof beginning with assumption $A$ and ending with $\false$, infer $\neg A$, discharging $A$.
- **$\neg E$:** from $A$ and $\neg A$, infer $\false$.
- **$\false E$:** from $\false$, infer any formula $A$.
- **$\leftrightarrow I$:** from $A\to B$ and $B\to A$, infer $A\leftrightarrow B$.
- **$\leftrightarrow E$:** from $A\leftrightarrow B$, infer either $A\to B$ or $B\to A$.
- **RAA:** from a subproof beginning with assumption $\neg A$ and ending with $\false$, infer $A$, discharging $\neg A$.

RAA is the only expressly classical rule. The restrictions on open assumptions are part of the calculus, not optional presentation advice.
