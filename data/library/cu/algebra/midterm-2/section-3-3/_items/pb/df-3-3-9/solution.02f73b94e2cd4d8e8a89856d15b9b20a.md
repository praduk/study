
Let $|G|=p^am$ with $p\nmid m$, let $P\le G$ have order $p^a$, and let $N\nsubg G$ have order $p^bn$ with $p\nmid n$. Prove $|P\cap N|=p^b$ and $|PN/N|=p^{a-b}$.

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

By Lagrange, $|P\cap N|= p^c$ for some $c\le a$.  By second isomorphism theorem
$$
NP/N \isoto P/N\cap P,
$$
so
$$
|NP| = \frac{|N||P|}{|N\cap P|} = p^{a+b-c}n.
$$

Because $NP$ is a subgroup of $G$, $|NP|$ divides $|G|$ so
$$
p^{a+b-c}n \mid p^am
$$
Because $p$ does not divide $n$ or $m$, we have
$$
a+b-c \le a \implies b \le c.
$$

Because $P$ is a subgroup of $NP$, $|P|$ divides $|NP|$ so
$$
p^a \mid p^{a+b-c}
$$
so
$$
a \le a+b-c \implies c \le b.
$$
Therefore $c=b$.

Then $|PN/N| = |P/N\cap P| = $p^{a-b}$.

**Foundations:** @cu:algebra:midterm-2:theorems:th:first-isomorphism, @cu:algebra:midterm-2:theorems:th:second-isomorphism, @cu:algebra:midterm-2:theorems:th:correspondence, @cu:algebra:midterm-2:theorems:th:product-order.
