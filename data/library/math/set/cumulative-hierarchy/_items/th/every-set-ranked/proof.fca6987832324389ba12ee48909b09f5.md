First, transfinite induction on $\beta$ shows that every $V_\beta$ is transitive and that $V_\alpha\subseteq V_\beta$ for $\alpha\le\beta$. At a successor stage, transitivity follows because members of subsets of $V_\alpha$ remain in $V_\alpha$; at a limit, it follows from taking a union of nested transitive stages.

Apply Set Induction to the assertion “$x$ lies in some hierarchy stage.” Assume it holds for every $y\in x$. For each $y\in x$, choose the least ordinal $r_y$ with $y\subseteq V_{r_y}$; this choice is definable and Replacement collects the $r_y$. Let

$$
\alpha=\sup\{r_y+1:y\in x\}.
$$

Then every $y\in x$ lies in $V_{r_y+1}\subseteq V_\alpha$. Hence $x\subseteq V_\alpha$, so $x\in\mathcal{P}(V_\alpha)=V_{\alpha+1}$. Set Induction proves the assertion for all $x$.

The ordinals are well-ordered, so the least $\alpha$ with $x\subseteq V_\alpha$ exists; this is $\operatorname{rank}(x)$. Taking the least bound in the preceding construction gives
$\operatorname{rank}(x)=\sup_{y\in x}(\operatorname{rank}(y)+1)$. Thus every set, and only sets, appears at some $V$-stage.
