

```tikzcd
\begin{tikzcd}
	& G & \\
	& NP \\
	N && P \\
	& {N\cap P}
	\arrow[no head, from=1-2, to=2-2]
	\arrow[no head, from=2-2, to=3-3]
	\arrow["\shortmid"{marking}, no head, from=3-1, to=2-2]
	\arrow["\shortmid"{marking}, no head, from=3-3, to=4-2]
	\arrow[no head, from=4-2, to=3-1]
\end{tikzcd}
```



Because $P\cap N\le P$, its order is a power $p^c$. Since it is also a subgroup of $N$, Lagrange gives $c\le b$. Normality of $N$ makes $PN$ a subgroup, and the product-order formula gives

$$
|PN|=\frac{|P||N|}{|P\cap N|}=p^{a+b-c}n.
$$

This subgroup order divides $|G|=p^am$. Since $p\nmid n,m$, the exponent of $p$ in its order cannot exceed $a$. Hence $a+b-c\le a$, or $b\le c$. Together with $c\le b$, this forces $c=b$.

Therefore $|P\cap N|=p^b$. The second isomorphism theorem gives

$$
PN/N\cong P/(P\cap N),
$$

so its order is $p^a/p^b=p^{a-b}$. In particular $P\cap N$ has the largest possible $p$-power order in $N$, and $PN/N$ has the largest possible $p$-power order in $G/N$.

**Technique:** introduce an unknown exponent for the intersection; Lagrange bounds it in one direction and the product formula in the other. No Sylow existence theorem is needed because $P$ is already supplied.

**Foundations:** @cu:algebra:midterm-2:theorems:th:first-isomorphism, @cu:algebra:midterm-2:theorems:th:second-isomorphism, @cu:algebra:midterm-2:theorems:th:correspondence, @cu:algebra:midterm-2:theorems:th:product-order.
