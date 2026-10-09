Let $S_n$ act naturally on $\{1,\ldots,n\}$.

(a) Action on the $k$-element subsets.

The action is
$$
\sigma\cdot A=\{\sigma(a):a\in A\}.
$$

Suppose first that $1\leq k<n$. We show that the action is faithful. Let
$\sigma\in S_n$ be nonidentity. Then there exists some $i$ such that
$$
\sigma(i)=j\neq i.
$$
Since $k<n$, we can choose a $k$-element subset $A$ such that
$$
i\in A
\qquad\text{and}\qquad
j\notin A.
$$
But $i\in A$ implies
$$
j=\sigma(i)\in \sigma(A).
$$
Since $j\notin A$, we have
$$
\sigma(A)\neq A.
$$
Thus every nonidentity element of $S_n$ acts nontrivially, so the action is faithful.

If $k=n$, there is only one $n$-element subset,
$$
\{1,\ldots,n\}.
$$
Every $\sigma\in S_n$ fixes this subset, so the kernel is all of $S_n$. Hence
the action is faithful only when $S_n$ is trivial, i.e. when $n=1$.

Therefore, the action on $k$-element subsets is faithful exactly when
$$
k<n,
$$
together with the trivial case $n=k=1$.


(b) Action on ordered $k$-tuples.

The action is coordinatewise:
$$
\sigma\cdot(a_1,\ldots,a_k)
=
(\sigma(a_1),\ldots,\sigma(a_k)).
$$

Let $\sigma\in S_n$ be nonidentity. Choose $i$ such that
$$
\sigma(i)\neq i.
$$
Since $k\geq 1$, consider, for example, the tuple
$$
(i,i,\ldots,i).
$$
Then
$$
\sigma\cdot(i,i,\ldots,i)
=
(\sigma(i),\sigma(i),\ldots,\sigma(i))
\neq
(i,i,\ldots,i).
$$
Thus every nonidentity permutation acts nontrivially.

Therefore, the action on ordered $k$-tuples is faithful for every
$$
1\leq k\leq n.
$$

In summary:

$$
\boxed{
\begin{aligned}
\text{(a)}\;&\text{faithful for }1\leq k<n,
\text{ and also trivially for }n=k=1;\\
\text{(b)}\;&\text{faithful for every }1\leq k\leq n.
\end{aligned}
}
$$
