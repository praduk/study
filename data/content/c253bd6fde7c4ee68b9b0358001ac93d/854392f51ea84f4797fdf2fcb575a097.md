First eliminate $\to$ and $\leftrightarrow$ recursively. Replace $A\to B$ by $\neg A\lor B$, and replace $A\leftrightarrow B$ by $(A\land B)\lor(\neg A\land\neg B)$, after recursively processing $A$ and $B$. The equivalences in @math:prop:semantics:th:fundamental-equivalences and replacement in @math:prop:semantics:th:replacement-equivalents show that the result is equivalent to the original and uses only $\neg,\land,\lor$ and constants.

Now define two transformations $N^+(A)$ and $N^-(A)$ on such formulas, intended to be equivalent to $A$ and $\neg A$. On atoms, set $N^+(p)=p$ and $N^-(p)=\neg p$. Set $N^+(\true)=\true$, $N^-(\true)=\false$, $N^+(\false)=\false$, and $N^-(\false)=\true$. Put

$$N^+(\neg A)=N^-(A),\qquad N^-(\neg A)=N^+(A),$$

$$N^+(A\land B)=N^+(A)\land N^+(B),\qquad N^-(A\land B)=N^-(A)\lor N^-(B),$$

$$N^+(A\lor B)=N^+(A)\lor N^+(B),\qquad N^-(A\lor B)=N^-(A)\land N^-(B).$$

A simultaneous structural induction, using double negation and De Morgan equivalences, proves $N^+(A)\equiv A$ and $N^-(A)\equiv\neg A$. The displayed recursion leaves negation only on atoms, so $N^+(A)$ is NNF. Applying this to the implication-free result proves the theorem.
