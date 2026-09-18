Suppose $G$ acts on $B$, $b\in B$, and $A\subseteq B$.
The **point stabilizer** is $G_b=\{g:g\cdot b=b\}$. Following the lecture notation, the **pointwise stabilizer** is

$$
\Stab_G(A)=\{g\in G:g\cdot a=a\text{ for every }a\in A\}.
$$

The lecture's **weak stabilizer** is the usual **setwise stabilizer**:

$$
\WStab_G(A)=\{g\in G:gA=A\}.
$$

Equivalently require both $gA\subseteq A$ and $g^{-1}A\subseteq A$. For infinite $A$, one inclusion alone need not give equality. The pointwise stabilizer is contained in the setwise stabilizer.
Example: $(12)$ preserves $\{1,2\}$ setwise but does not fix it pointwise. The **kernel of the action** is $\Stab_G(B)=\bigcap_{b\in B}G_b$.
