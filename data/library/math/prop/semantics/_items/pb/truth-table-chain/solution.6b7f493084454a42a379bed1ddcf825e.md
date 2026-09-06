The complete table is

$$\begin{array}{ccc|cc|c|c|c}p&q&r&p\to q&q\to r&(p\to q)\land(q\to r)&p\to r&F\\\hline 1&1&1&1&1&1&1&1\\1&1&0&1&0&0&0&1\\1&0&1&0&1&0&1&1\\1&0&0&0&1&0&0&1\\0&1&1&1&1&1&1&1\\0&1&0&1&0&0&1&1\\0&0&1&1&1&1&1&1\\0&0&0&1&1&1&1&1\end{array}$$

The final column is always $1$, so $F$ is a tautology. Semantically, when both premises in the antecedent are true and $p$ is true, the first conditional forces $q$ and the second forces $r$; hence $p\to r$ cannot be false.
