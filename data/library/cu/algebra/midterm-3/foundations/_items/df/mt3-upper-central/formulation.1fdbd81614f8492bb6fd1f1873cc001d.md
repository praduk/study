For any group $G$, define $Z_0(G)=1$. Recursively, $Z_{i+1}(G)$ is the full inverse image of the center of $G/Z_i(G)$ under the quotient map; thus

$$
Z_{i+1}(G)/Z_i(G)=Z(G/Z_i(G)).
$$

Equivalently,

$$
Z_{i+1}(G)=\{x\in G:[x,g]\in Z_i(G)\text{ for every }g\in G\}.
$$

The ascending sequence $1=Z_0(G)\le Z_1(G)\le\cdots$ is the **upper central series**, with $Z_1(G)=Z(G)$. These are subgroups of $G$, not just subgroups of a quotient. Their characteristicity is proved in @mt3-series-functorial.
