**Construct a prime.** Choose one variable $s_i$ from each pair $\{x_{2i-1},x_{2i}\}$ and call its partner $t_i$. Write bars for classes in $A/I$. Let $P$ be the @[ideal generated]mt4-principal-ideal by the classes $\bar s_i$. Setting every $s_i$ to zero and fixing the $t_i$ defines a @[ring homomorphism]mt4-ring-homomorphism from $A$ onto $\Z[t_1,t_2,\ldots]$. Every generator $s_it_i$ of $I$ goes to zero, so representatives differing by an element of $I$ have the same image. This gives a surjection on the @[quotient]mt4-quotient-ring,

$$
A/I\longrightarrow\Z[t_1,t_2,\ldots].
$$

Its kernel is $P$. Indeed, evaluating the unique @[monomial expansion]mt4-polynomials-several-variables kills precisely the terms divisible by some $s_i$. The remaining monomials are distinct, so their sum is zero only if their coefficients all vanish. The target is a domain by @[the polynomial domain theorem]mt4-polynomial-domains. Thus $(A/I)/P$ is a domain by the @[first isomorphism theorem]mt4-first-isomorphism, and $P$ is prime by the @[quotient criterion]mt4-prime-quotient-domain.

**Prove minimality.** Let $Q$ be a prime ideal with $Q\subseteq P$. For each $i$, the element $\bar t_i$ maps to the indeterminate $t_i$, so $\bar t_i\notin P$ and hence $\bar t_i\notin Q$. But $\bar s_i\bar t_i=0\in Q$. By @[primality]mt4-prime-ideal, $\bar s_i\in Q$ for every $i$. Thus $P\subseteq Q$, giving $Q=P$. This is exactly @[minimality]mt4-minimal-prime.

**Distinguish infinitely many.** For each $j\ge1$, choose the even variable in pair $j$ and the odd variable in every other pair. The resulting ideal $P_j$ contains $\bar x_{2j}$. For $k\ne j$, this variable survives in the target used for $P_k$, so $\bar x_{2j}\notin P_k$. Thus the $P_j$ are pairwise distinct.
