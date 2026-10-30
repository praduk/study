Let $G$ a group and $|G|=mn$.  Let
$$
\aligned{
\pi: G&\to S_G \\
g &\mapsto (x \mapsto gx).
}
$$
Let $x\in G$ so that $|x|=n$.  Let $H=\genby{x}$.  Then $|H|=n$.  Partition $G$ into right-cosets $Hg$.  The size of each coset is $|H|=n$.  Because
$$
\pi(x) Hg_i = xHg_i = Hg_i,
$$
$\pi(x)$ permutes the elements in each $Hg_i$ with the $n$-cycle
$$
p_i = (g_i xg_i \cdots x^{n-1} g_i).
$$
And $\pi(x)$ is a product of these cycles.

Then apply the sign homomorphism to see
$$
\sigma(\pi(x)) = (-1)^{m(n-1)}.
$$
The sign is -1 (odd) iff $m$ and $n-1$ are odd.
