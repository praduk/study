Let $S$ be a set.  The free group $F(S)$ is the unique group up to isomorphism such that

1. There exists an injective function $\iota: S\to F(S)$.
2. For every function $\tau:S\to G$ for every group $G$, there exists a unique homomorphism $\pi:F(S)\to G$ such that $\tau = \pi \circ \iota$.



```tikzcd
\begin{tikzcd}
	S & {F(S)} \\
	& G
	\arrow["\iota", hook, from=1-1, to=1-2]
	\arrow["\tau"', from=1-1, to=2-2]
	\arrow["{\exists!\pi}", dashed, from=1-2, to=2-2]
\end{tikzcd}
```
