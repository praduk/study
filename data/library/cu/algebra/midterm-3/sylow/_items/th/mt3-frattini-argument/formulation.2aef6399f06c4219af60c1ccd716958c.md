If $G$ is finite, $N\trianglelefteq G$, and $P\in\Syl_p(N)$, then

$$
G=N N_G(P),\qquad [G:N]=[N_G(P):N_G(P)\cap N].
$$

In particular $[G:N]$ divides $|N_G(P)|$. The Sylow hypothesis is **inside $N$**; $P$ need not be Sylow in $G$.

**Trigger:** a normal subgroup and one of its Sylow subgroups → adjust conjugation by an element of the normal subgroup. Uses include proving all-maximal-normal implies nilpotence, lifting Sylow normalizers through coprime quotients, and proving the Frattini subgroup is nilpotent.



```tikzcd
\begin{tikzcd}
	& {G=NN_G(P)} & \\
	N && {N_G(P)} \\
	& P
	\arrow["\shortmid"{marking}, no head, from=1-2, to=2-1]
	\arrow[no head, from=1-2, to=2-3]
	\arrow[no head, from=2-1, to=3-2]
	\arrow["\shortmid"{marking}, no head, from=2-3, to=3-2]
\end{tikzcd}
```

```tikzcd
\begin{tikzcd}
	& {G=NN_G(P)} & \\
	N && {N_G(P)} \\
	& N_G(P) \cap N
	\arrow["\shortmid"{marking}, no head, from=1-2, to=2-1]
	\arrow[no head, from=1-2, to=2-3]
	\arrow[no head, from=2-1, to=3-2]
	\arrow["\shortmid"{marking}, no head, from=2-3, to=3-2]
\end{tikzcd}
```
