Soundness gives the right-to-left direction. For the other direction, suppose $\Gamma\models A$. Let $P$ be the finite union of the atom sets of $A$ and all members of $\Gamma$. Fix a finite assignment $a:P\to\{0,1\}$.

If $a(G)=1$ for every $G\in\Gamma$, choose a total valuation extending $a$. It satisfies $\Gamma$, so it satisfies $A$; evaluation by a finite assignment agrees with evaluation by every extension, hence $a(A)=1$. The signed-valuation lemma then gives $\Delta_a(P)\vdash A$. If instead $a(G)=0$ for some $G\in\Gamma$, that lemma gives $\Delta_a(P)\vdash\neg G$. From the premise $G$, derive $\false$ and then $A$ by $\false E$. Thus for every finite assignment $a$ on $P$,

$$\Gamma\cup\Delta_a(P)\vdash A.$$

Enumerate $P=\{p_1,\ldots,p_n\}$. Pair the $2^n$ derivations for assignments that differ only on $p_n$. Each pair gives a derivation of $A$ from the common literals together with $p_n$ in one branch and $\neg p_n$ in the other. Since $\vdash p_n\lor\neg p_n$, one application of $\lor E$ removes that last literal choice. Repeat with $p_{n-1},\ldots,p_1$. After finitely many case eliminations, no assignment literals remain and $\Gamma\vdash A$. If $P$ is empty, the unique assignment on $P$ supplies a derivation with no assignment literals. Hence semantic consequence from finite premises implies derivability.
