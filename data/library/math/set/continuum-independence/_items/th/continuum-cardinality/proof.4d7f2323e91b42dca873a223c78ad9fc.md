Characteristic functions give a bijection
$\mathcal{P}(\omega)\to2^\omega$.

For an injection $\mathcal{P}(\omega)\to\mathbb R$, send $S\subseteq\omega$ to

$$
x_S=\sum_{n\in S}\frac{2}{3^{n+1}}.
$$

If $S\ne T$, let $k$ be their least point of difference and assume $k\in S\setminus T$. The contribution $2/3^{k+1}$ at $k$ is larger than the sum
$\sum_{n>k}2/3^{n+1}=1/3^{k+1}$ of all possible later opposing contributions. Hence $x_S\ne x_T$.

For an injection $\mathbb R\to\mathcal{P}(\omega)$, fix an enumeration $(q_n)$ of $\mathbb Q$ and send

$$
x\longmapsto\{n\in\omega:q_n<x\}.
$$

If $x<y$, density of $\mathbb Q$ supplies $q_n$ with $x<q_n<y$; then $n$ belongs to the set for $y$ but not to the set for $x$. Thus the map is injective. Cantor--Schröder--Bernstein now yields
$\mathbb R\approx\mathcal{P}(\omega)$, and the characteristic-function bijection supplies the remaining equality.
