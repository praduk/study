Assume Foundation and suppose the progressive hypothesis holds but $\varphi(a)$ fails for some $a$. Form the transitive closure of $\{a\}$ by setting
$T_0=\{a\}$, $T_{n+1}=\bigcup T_n$, and
$T=\bigcup_{n\in\omega}T_n$. Recursion and Replacement make $T$ a transitive set. By Separation, the set
$B=\{x\in T:\neg\varphi(x)\}$ is nonempty. Foundation gives $b\in B$ with $b\cap B=\varnothing$. Since $T$ is transitive, every $y\in b$ lies in $T$; minimality says every such $y$ satisfies $\varphi$. Progressiveness then gives $\varphi(b)$, contradicting $b\in B$.

Conversely, assume Set Induction and let $A$ be nonempty. Suppose $A$ had no $\in$-minimal member, so every $x\in A$ had some $y\in x\cap A$. Use Set Induction with
$\varphi(x)$ meaning $x\notin A$. If every member $y$ of $x$ is outside $A$ and $x$ were in $A$, the no-minimal-member assumption would give some $y\in x\cap A$, a contradiction. Thus progressiveness holds, and Set Induction says every set is outside $A$, contradicting that $A$ is nonempty. Hence Foundation holds.
