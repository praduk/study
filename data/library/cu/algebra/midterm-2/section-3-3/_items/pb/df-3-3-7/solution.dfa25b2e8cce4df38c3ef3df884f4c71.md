Let

$$
\aligned{
\phi: G &\to G/M \times G/N \\
g &\mapsto (gM, gN).
}
$$

Because $M$ and $N$ are normal in $G$, this is a well defined group homomorphism:
$$
\phi(g_1g_2) = (g_1g_2 M, g_1 g_2N) = (g_1 M, g_1 N) (g_2 M, g_2 N) = \phi(g_1)\phi(g_2).
$$

We have $\ker \phi = \set{g\in G: g\in M \text{ and } g\in N} = M \cap N$.

To show $\phi$ is surjective, let $(g_1 M, g_2 N)\in G/M \times G/N$.  Because $G = MN$,
$$
\aligned{
g_1 &= m_1 n_1 \\
g_2 &= m_2 n_2.
}
$$
Choose $g = n_1 n_1^{-1} m_2 n_1$.  Then
$$
\aligned{
\phi(g) &= (g M, gN) \\
&= (n_1 M, m_2 N) \\
&= (n_1 m_1 M, m_2 n_2 N) \\
&= (g_1 M, g_2 N).
}
$$

By the first isomorphism theorem $G/M\cap N \isoto G/M \times G/N$.
