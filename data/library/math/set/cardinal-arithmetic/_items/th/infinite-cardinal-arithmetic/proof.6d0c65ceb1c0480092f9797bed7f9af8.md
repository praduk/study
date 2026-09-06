It suffices to prove $|\kappa\times\kappa|=\kappa$. Proceed by induction over infinite cardinals. Well-order $\kappa\times\kappa$ first by
$\max\{\alpha,\beta\}$ and then lexicographically within each level. The predecessors of $(\alpha,\beta)$ lie inside
$(\gamma+1)\times(\gamma+1)$, where $\gamma=\max\{\alpha,\beta\}<\kappa$.

If $\kappa=\aleph_0$, each such predecessor set is finite. For larger $\kappa$, let $\rho=\max(\aleph_0,|\gamma|)<\kappa$. By the induction hypothesis,
$|\rho\times\rho|=\rho$, so every initial segment of the displayed well-order has cardinality strictly below $\kappa$.

Let $\tau$ be its ordinal order type. If $\tau$ had more than $\kappa$ elements, the element in position $\kappa$ would have $\kappa$ predecessors, contrary to the preceding paragraph. Thus $|\kappa\times\kappa|\le\kappa$. The map
$\alpha\mapsto(\alpha,0)$ gives the reverse injection, so Cantor--Schröder--Bernstein yields equality.

Since $2\le\kappa$, the tagged union of two copies of $\kappa$ injects into $\kappa\times\kappa$, while one copy injects into the tagged union. Hence $\kappa+\kappa=\kappa$. For general infinite $\kappa,\lambda$, assume $\kappa\le\lambda$; both sum and product lie between $\lambda$ and $\lambda\cdot\lambda=\lambda$.
