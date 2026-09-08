An algebra of sets on $X$ contains $X$ and is closed under complements in $X$ and finite unions. A premeasure is a map $\mu_0:\mathcal A_0\to[0,\infty]$ with $\mu_0(\varnothing)=0$ satisfying countable additivity whenever a disjoint union of members belongs to $\mathcal A_0$. Define

$$
\mu^*(E)=\inf\left\{\sum_n\mu_0(A_n):E\subseteq\bigcup_n A_n,\ A_n\in\mathcal A_0\right\}.
$$

This construction extends $\mu_0$ to a measure on $\sigma(\mathcal A_0)$. If $X$ is a countable union of sets in $\mathcal A_0$ of finite premeasure, this extension is unique on $\sigma(\mathcal A_0)$.

The proof of the extension and uniqueness assertions is not included. See Hunter, [Measure Theory, Section 5.2](https://www.math.ucdavis.edu/~hunter/measure_theory/measure_notes.pdf). Uniqueness on the generated @[sigma algebra]math:analysis:measure-construction:df:measure-space should not be confused with a choice of completion.
