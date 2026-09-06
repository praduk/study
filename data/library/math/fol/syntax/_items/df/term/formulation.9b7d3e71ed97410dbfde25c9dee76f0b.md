The set of $L$-terms is generated recursively. Every variable and constant symbol is a term. If $f$ is an $n$-ary function symbol and $t_1,…,t_n$ are terms, then $f(t_1,…,t_n)$ is a term. Nothing else is a term.

A term is closed when it contains no variables. The variables occurring in a term are defined recursively in the evident way. The depth of a variable or constant is $0$, and the depth of $f(t_1,…,t_n)$ is $1+\max_i\operatorname{depth}(t_i)$.
