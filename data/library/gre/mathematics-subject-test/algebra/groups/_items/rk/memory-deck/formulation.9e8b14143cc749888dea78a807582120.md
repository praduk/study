## Definitions and quick tests

A group has associativity, identity, and inverses. A nonempty subset $H\subseteq G$ is a subgroup iff $ab^{-1}\in H$ for all $a,b\in H$. A finite nonempty subset closed under multiplication is automatically a subgroup.

For a cyclic group $G=\langle g\rangle$ of order $n$,

$$
|g^k|=\frac n{\gcd(n,k)},
$$

and the number of generators is $\varphi(n)$. Every subgroup of a cyclic group is cyclic, with one subgroup for each positive divisor of $n$.

## Lagrange, cosets, and normality

If $H\le G$ and $G$ is finite,

$$
|G|=[G:H]|H|,
$$

so element and subgroup orders divide $|G|$. The converse—every divisor occurs as a subgroup order—is false in general.

$N\triangleleft G$ iff $gNg^{-1}=N$ for all $g$. Kernels are normal. Every subgroup of index $2$ is normal. Subgroups of an abelian group are normal, but subgroups of a general nonabelian group need not be.

## Homomorphisms

$$
G/\ker\phi\cong\operatorname{im}\phi.
$$

For finite groups,

$$
|G|=|\ker\phi|\,|\operatorname{im}\phi|.
$$

A homomorphism from a cyclic group is determined by the image of a generator, and that image's order must divide the generator's order.

## Permutations

Write permutations as disjoint cycles. Disjoint cycles commute; the permutation order is the least common multiple of the cycle lengths. A $k$-cycle has sign $(-1)^{k-1}$. Hence $|S_n|=n!$ and $|A_n|=n!/2$ for $n\ge2$.

## Actions

For an action of $G$ on $X$,

$$
|Gx|=[G:G_x],
$$

where $Gx$ is the orbit and $G_x$ the stabilizer. Burnside's counting lemma, when needed, says the number of orbits is

$$
\frac1{|G|}\sum_{g\in G}|\operatorname{Fix}(g)|.
$$

Conjugation gives the class equation

$$
|G|=|Z(G)|+\sum_i[G:C_G(x_i)].
$$

## Trap list

Do not confuse element order with group order, left cosets with normality, or a one-sided converse of Lagrange with the theorem itself. In permutation products, state the composition convention and apply it consistently.
