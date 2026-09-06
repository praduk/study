Proceed by structural induction on $A$, with every truth claim in this proof evaluated under the fixed finite assignment $a$. For an atom, the required atom or negated atom is a member of $\Delta_a(P)$. The formula $\true$ follows by $\true I$. Since $\false$ is never true, only its false case occurs; assume $\false$ and reiterate it, then $\neg I$ gives $\neg\false$.

If $A=\neg B$ and $A$ is true, then $B$ is false, so the induction hypothesis already gives $\neg B$, which is $A$. If $A$ is false, then $B$ is true; the induction hypothesis gives $B$. Assuming $\neg B$ produces $\false$, so $\neg I$ gives $\neg\neg B=\neg A$.

If $A=B\land C$ is true, both children are true; derive each by induction and apply $\land I$. If it is false, at least one child is false. Suppose $B$ is false; induction gives $\neg B$. Assume $B\land C$, use $\land E$ to get $B$, derive $\false$, and close by $\neg I$. The case in which $C$ is false is symmetric.

If $A=B\lor C$ is true, at least one child is true; derive that child by induction and use $\lor I$. If it is false, induction gives both $\neg B$ and $\neg C$. Assume $B\lor C$. By $\lor E$, the $B$ case contradicts $\neg B$ and the $C$ case contradicts $\neg C$, so both yield $\false$. Close by $\neg I$ to obtain $\neg(B\lor C)$.

If $A=B\to C$ is true, either $B$ is false or $C$ is true. In the first case induction gives $\neg B$; assume $B$, derive $\false$, use $\false E$ to obtain $C$, and close by $\to I$. In the second case induction gives $C$; assume $B$, reiterate $C$, and close by $\to I$. If the implication is false, $B$ is true and $C$ false. Induction gives $B$ and $\neg C$. Assume $B\to C$, infer $C$, derive $\false$, and close by $\neg I$.

If $A=B\leftrightarrow C$ is true, the child values agree. If both are true, induction gives $B,C$; use each available conclusion inside the appropriate conditional subproof to derive $B\to C$ and $C\to B$, then apply $\leftrightarrow I$. If both are false, induction gives $\neg B,\neg C$; from an assumed $B$ derive $\false$ and then $C$, yielding $B\to C$, and symmetrically yield $C\to B$; apply $\leftrightarrow I$. If the biconditional is false, the child values differ. Suppose $B$ is true and $C$ false. Induction gives $B$ and $\neg C$. Assume $B\leftrightarrow C$, use $\leftrightarrow E$ to get $B\to C$, infer $C$, and contradict $\neg C$; $\neg I$ yields $\neg(B\leftrightarrow C)$. The other unequal case is symmetric.

All formula constructors have been covered, so the simultaneous true/false claim follows.
