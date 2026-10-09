Let $G$ be finite, $H\le G$, and $N\nsubg G$. If $\gcd(|H|,[G:N])=1$, prove $H\le N$.

If we show $[H:N\cap H]=1$, then $H=N\cap H$ so $H\subg N$.

Because $N\nsubg G$, $H \subg N_G(N)$, we can apply second isomorphism theorem
$$
H/H\cap N \isoto HN/N.
$$

Because
$$
|H| = [H:N\cap H]|N\cap H|.
$$
$[H:N\cap H]$ divides $|H|$ so
$$
\gcd([H:N\cap H], [G:N]) = 1.
$$

But
$$
[G:N] = [G:HN][HN:N] = [G:HN][H:N\cap H].
$$

So $[H:N\cap H]$ divides $[G:N]$.  But if $[H:N\cap H]$ divides $[G:N]$ and $\gcd([H:N\cap H],[G:N])=1$, then $[H:N\cap H]=1$.
