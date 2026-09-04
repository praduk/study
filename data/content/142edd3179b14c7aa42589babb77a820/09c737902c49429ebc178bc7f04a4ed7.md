A variable assignment in $𝔐$ is a map $g:\mathrm{Var}→M$. Write $g[x↦a]$ for the assignment that sends $x$ to $a$ and otherwise agrees with $g$.

The value $t^𝔐[g]$ of a term is defined recursively: $x^𝔐[g]=g(x)$, $c^𝔐[g]=c^𝔐$, and $f(t_1,…,t_n)^𝔐[g]=f^𝔐(t_1^𝔐[g],…,t_n^𝔐[g])$. A closed term has the same value under every assignment.
