Let
$$
\sigma=(a_1\ a_2\ \cdots\ a_m).
$$
By definition of cycle notation,
$$
\sigma(a_k)=a_{k+1},
$$
where the indices are read cyclically modulo $m$; in particular, $\sigma(a_m)=a_1$.

We prove by induction on $i$ that
$$
\sigma^i(a_k)=a_{k+i}.
$$

For $i=1$, this follows immediately from the definition of $\sigma$:
$$
\sigma(a_k)=a_{k+1}.
$$

Now suppose that for some $i\geq 1$,
$$
\sigma^i(a_k)=a_{k+i}.
$$
Then
$$
\sigma^{i+1}(a_k)
=\sigma\bigl(\sigma^i(a_k)\bigr)
=\sigma(a_{k+i})
=a_{k+i+1}.
$$
Thus, by induction,
$$
\sigma^i(a_k)=a_{k+i}
$$
for every $i\in\{1,\ldots,m\}$, with indices read cyclically modulo $m$.

In particular, when $i=m$,
$$
\sigma^m(a_k)=a_{k+m}=a_k
$$
for every $k\in\{1,\ldots,m\}$.

Moreover, $\sigma$ fixes every element not among $a_1,\ldots,a_m$, so $\sigma^m$ fixes every element. Hence
$$
\sigma^m=\operatorname{id}.
$$
Therefore $|\sigma|$ divides $m$.

To show that the order is exactly $m$, suppose $1\leq i<m$. Then
$$
\sigma^i(a_1)=a_{1+i}\neq a_1,
$$
since $a_1,\ldots,a_m$ are distinct and $1+i$ is not congruent to $1$ modulo $m$. Thus
$$
\sigma^i\neq\operatorname{id}
$$
for every $1\leq i<m$.

Consequently, the smallest positive integer $i$ such that $\sigma^i=\operatorname{id}$ is $m$. Therefore
$$
|\sigma|=m.
$$
