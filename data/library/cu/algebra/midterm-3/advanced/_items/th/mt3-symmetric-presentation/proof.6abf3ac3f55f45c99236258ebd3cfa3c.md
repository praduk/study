**Definitions and result used:** @mt3-presentations and @mt3-free-maps.

Adjacent swaps generate every permutation by successively moving each desired entry into position. They satisfy the displayed relations, so the abstract presented group $W_n$ maps onto $S_n$. We prove $|W_n|\le n!$, which forces this map to be an isomorphism.

Let $H=\langle t_1,\ldots,t_{n-2}\rangle$. By induction $|H|\le(n-1)!$, since it is a quotient of $W_{n-1}$. Set $r_n=1$ and $r_k=t_{n-1}t_{n-2}\cdots t_k$ for $1\le k<n$. The relations give the following rewrites when $k<n$:

$$
r_kt_i=\begin{cases}
t_i r_k&i<k-1,\\
r_{k-1}&i=k-1,\\
r_{k+1}&i=k,\\
t_{i-1}r_k&i>k.
\end{cases}
$$

For the last rule, commute distant generators and use the braid relation $t_it_{i-1}t_i=t_{i-1}t_it_{i-1}$, which follows from the involution and cube relations. Also $r_nt_i=t_i\in H$ if $i<n-1$, and $r_nt_{n-1}=r_{n-1}$.

Thus the union of the $n$ sets $Hr_k$ contains $1$ and is closed under right multiplication by every generator. It is all of $W_n$, so $|W_n|\le n|H|\le n!$. The base $W_1=1$ (or directly $|W_2|\le2$) starts the induction. Since $|S_n|=n!$, the surjection is an isomorphism.
