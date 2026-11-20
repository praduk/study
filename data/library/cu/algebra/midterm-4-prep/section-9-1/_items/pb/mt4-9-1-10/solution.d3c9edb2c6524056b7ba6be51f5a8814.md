**Strategy.** In the quotient, the product of each pair of variables is zero. A prime ideal must contain at least one variable from each pair. Choose exactly one from each pair, prove that the resulting ideal is prime and minimal, then vary the choices.

**1. Construct a candidate.** Write bars for classes in $A/I$. From each pair $\{x_{2i-1},x_{2i}\}$ choose $s_i$ and call its partner $t_i$. Let $P$ be the @[ideal generated]mt4-principal-ideal by all the $\bar s_i$. Setting every $s_i$ to zero and fixing the $t_i$ defines a @[ring homomorphism]mt4-ring-homomorphism on $A$. It kills every generator $s_it_i$ of $I$, so it induces a surjection from the @[quotient ring]mt4-quotient-ring,

$$
\varphi\colon A/I\longrightarrow\Z[t_1,t_2,\ldots].
$$

**2. Show $P$ is prime.** The kernel of $\varphi$ consists exactly of $P$. Indeed, in the @[monomial expansion]mt4-polynomials-several-variables of a representative, substitution erases the monomials containing a chosen $s_i$. All other monomials remain distinct. Thus the image is zero exactly when every term of the representative contains some $s_i$, which is exactly membership in $P$ after passing to classes.

By the @[first isomorphism theorem]mt4-first-isomorphism, $(A/I)/P$ is isomorphic to $\Z[t_1,t_2,\ldots]$. This ring is a @[domain]mt4-polynomial-domains because any two nonzero polynomials lie in a polynomial ring over $\Z$ in finitely many variables, where their product is nonzero. The @[quotient criterion]mt4-prime-quotient-domain now gives primality.

**3. Show $P$ is minimal.** Suppose $Q\subseteq P$ is prime. For each $i$, $\varphi(\bar t_i)=t_i\ne0$, so $\bar t_i\notin P$ and hence $\bar t_i\notin Q$. But $\bar s_i\bar t_i=0\in Q$. By @[primality]mt4-prime-ideal, $\bar s_i\in Q$. Thus $Q$ contains every generator of $P$, forcing $Q=P$. This proves @[minimality]mt4-minimal-prime.

**4. Produce infinitely many different ideals.** For each $j\ge1$, choose the even variable in pair $j$ and the odd variable in every other pair. The resulting $P_j$ contains $\bar x_{2j}$. For $k\ne j$, that same variable survives substitution for $P_k$, so it lies outside $P_k$. The ideals $P_1,P_2,\ldots$ are pairwise distinct minimal primes.
