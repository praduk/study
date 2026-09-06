The **cumulative hierarchy** is defined by transfinite recursion:

$$
V_0=\varnothing,
\qquad
V_{\alpha+1}=\mathcal{P}(V_\alpha),
\qquad
V_\lambda=\bigcup_{\alpha<\lambda}V_\alpha
\quad(\lambda\text{ limit}).
$$

The stages are transitive and increasing: if $\alpha\le\beta$, then
$V_\alpha\subseteq V_\beta$.

Once it is proved that every set lies in some stage, the **rank** of $x$ is

$$
\operatorname{rank}(x)=
\min\{\alpha:x\subseteq V_\alpha\}
=\sup\{\operatorname{rank}(y)+1:y\in x\}.
$$

Then $x\in V_{\operatorname{rank}(x)+1}$. The symbol $V$ for “all sets” denotes the proper class $\bigcup_{\alpha\in\mathrm{Ord}}V_\alpha$, not a set-sized union.
