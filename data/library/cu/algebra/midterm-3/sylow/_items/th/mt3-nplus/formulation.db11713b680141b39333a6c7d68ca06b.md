Let $G$ be finite, $p\mid|G|$, and $k\ge1$. For every pair of distinct $P,Q\in \Syl_p(G)$ suppose
$$
p^k\mid [P:P\cap Q]
$$

Then
$$
n_p\equiv1\pmod{p^k}.
$$



```tikzcd
\begin{tikzcd}
	& G & \\
	P && Q \\
	& {P\cap Q}
	\arrow[no head, from=1-2, to=2-1]
	\arrow[no head, from=1-2, to=2-3]
	\arrow["{p^k}", no head, from=2-1, to=3-2]
	\arrow["{p^k}"', no head, from=2-3, to=3-2]
\end{tikzcd}
```



The hypothesis concerns **indices of intersections**, not merely the order of $G$. For $k=1$ it recovers the usual Sylow congruence. For larger $k$ it is an additional-hypothesis theorem.

Prerequisites: @[Group action, orbit, and stabilizer]cu:algebra:midterm-3:foundations:df:mt3-group-action, @[Orbit–stabilizer theorem]cu:algebra:midterm-3:foundations:th:mt3-actions, and @[Sylow normalizer lemma]cu:algebra:midterm-3:sylow:th:mt3-sylow-normalizer. The key observation is $N_P(Q)=P\cap Q$ whenever $Q$ is Sylow.
