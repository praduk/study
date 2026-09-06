A valuation $v$ **satisfies** a formula $A$, written $v\models A$, when $\llbracket A\rrbracket_v=1$. It satisfies a set $\Gamma$ of formulas, written $v\models\Gamma$, when $v\models G$ for every $G\in\Gamma$.

If $P\subseteq\mathsf{Prop}$ is finite, a **finite assignment on $P$** is a function $a:P\to\{0,1\}$. A total valuation $v$ **extends** $a$ when $v|_P=a$; every finite assignment has a total extension, for example by assigning $0$ to every atom outside $P$.

When $\operatorname{At}(A)\subseteq P$, extend $a$ recursively from atoms to $A$ by

$$a(\true)=1,\qquad a(\false)=0,\qquad a(\neg B)=1-a(B),$$

$$a(B\land C)=1\text{ iff }a(B)=a(C)=1,$$

$$a(B\lor C)=1\text{ iff }a(B)=1\text{ or }a(C)=1,$$

$$a(B\to C)=0\text{ iff }a(B)=1\text{ and }a(C)=0,$$

$$a(B\leftrightarrow C)=1\text{ iff }a(B)=a(C).$$

Write $\llbracket A\rrbracket_a:=a(A)$. For every total extension $v$ of $a$, a structural induction on $A$ gives

$$a(A)=\llbracket A\rrbracket_v,$$

so the chosen extension cannot affect the result. Write $a\models A$ when $a(A)=1$.

A **truth table** for formulas whose combined atom set is $P=\{p_1,\ldots,p_n\}$ lists the $2^n$ finite assignments $a:P\to\{0,1\}$ and the value $a(A)$ of each formula. Atoms outside $P$ do not affect any listed value.
