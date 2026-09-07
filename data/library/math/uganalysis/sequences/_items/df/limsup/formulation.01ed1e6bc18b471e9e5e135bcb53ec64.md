For a bounded real sequence define $s_n=\sup_{k\ge n}x_k$ and $i_n=\inf_{k\ge n}x_k$. Then

$$
\limsup_n x_n=\lim_n s_n,\qquad \liminf_n x_n=\lim_n i_n.
$$

These limits exist since $(s_n)$ decreases and $(i_n)$ increases. They are the largest and smallest subsequential limits. For $x_n=(-1)^n$, they are $1$ and $-1$. The same definitions extend to arbitrary real sequences using extended-real limits.

For the extremal-subsequence assertion, let $L=\limsup x_n$. Every subsequential limit is at most every sufficiently early tail supremum, hence at most $L$. Recursively choose $n_k>n_{k-1}$ with

$$
x_{n_k}>\sup_{j>n_{k-1}}x_j-1/k.
$$

The corresponding tail suprema tend to $L$, so the chosen values tend to $L$. Apply this argument to $-x_n$ to obtain the assertion for the limit inferior.
