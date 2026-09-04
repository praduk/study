Let $P$ be a finite set of atoms and let $a:P\to\{0,1\}$ be a finite assignment. Define the complete literal set

$$\Delta_a(P)=\{p\in P:a(p)=1\}\cup\{\neg p:p\in P,\ a(p)=0\}.$$

For every formula $A$ with $\operatorname{At}(A)\subseteq P$:

- if $a(A)=1$, then $\Delta_a(P)\vdash A$;
- if $a(A)=0$, then $\Delta_a(P)\vdash\neg A$.
