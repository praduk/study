The empty set and complements satisfy the defining identity immediately. If $A,B$ are measurable, first split an arbitrary $E$ by $A$, then split $E\setminus A$ by $B$. This yields
$\mu^*(E)\ge\mu^*(E\cap(A\cup B))+\mu^*(E\setminus(A\cup B))$
using subadditivity on the two pieces inside $A\cup B$. Hence finite unions, intersections, and differences are measurable.

For disjoint measurable $A_n$, repeated splitting gives

$$
\mu^*(E)\ge\sum_{n=1}^N\mu^*(E\cap A_n)+\mu^*(E\setminus A),\qquad A=\bigcup_n A_n.
$$

Let $N\to\infty$ and use $\mu^*(E\cap A)\le\sum_n\mu^*(E\cap A_n)$. The reverse Carathéodory inequality follows, so $A$ is measurable. Disjointizing arbitrary countable unions now proves sigma closure. With $E=A$, the same inequality and subadditivity give countable additivity. Finally, if $N$ has outer measure zero and $B\subseteq N$, then $\mu^*(E\cap B)=0$ and monotonicity yields $\mu^*(E)\ge\mu^*(E\setminus B)$. Together with subadditivity this proves that $B$ is measurable and null.
