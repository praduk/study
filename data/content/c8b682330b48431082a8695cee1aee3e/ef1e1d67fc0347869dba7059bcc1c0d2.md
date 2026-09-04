Treat each cardinal as its initial ordinal. There is an injection from the disjoint sum to the product: send $(i,\alpha)$ to the function that has value $\alpha$ at coordinate $i$ and value $\kappa_j$ at every coordinate $j\ne i$. This is legitimate because $\alpha<\kappa_i<\lambda_i$ and $\kappa_j<\lambda_j$. Images of different tagged summands differ at one of their tags, since the default value $\kappa_i$ is outside the range $\kappa_i$.

There is no surjection in the other direction. Let

$$
F:\bigsqcup_{i\in I}\kappa_i\longrightarrow\prod_{i\in I}\lambda_i
$$

be any function. For each $i$, the set

$$
C_i=\{F(i,\alpha)(i):\alpha<\kappa_i\}
$$

has cardinal at most $\kappa_i$, so it is a proper subset of $\lambda_i$. Because $\lambda_i$ is an ordinal, define without making any further choice

$$
b_i=\min(\lambda_i\setminus C_i).
$$

Replacement collects these uniquely defined values into the function
$b=(b_i)_{i\in I}$. It lies in the product and differs from every $F(i,\alpha)$ at coordinate $i$. Hence $F$ is not surjective. (The theorem is stated in ZFC so that the indexed cardinal operations have initial-ordinal values; the diagonal selection itself uses least elements, not an additional appeal to Choice.)

The injection plus nonexistence of a reverse equinumerosity gives the strict inequality.
