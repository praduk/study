For an invariant subspace $W\subseteq V$, choose a linear projection $p:V\to W$ restricting to the identity on $W$. Average it:

$$
\bar p=\frac1{|G|}\sum_{g\in G}\rho(g)p\rho(g)^{-1}.
$$

Each summand has image in $W$ and fixes $W$, so $\bar p$ also has image in $W$ and restricts to the identity there. Reindexing the sum shows $\bar p$ commutes with every $\rho(h)$. Hence its kernel is invariant and $V=W\oplus\ker\bar p$. Induction on dimension, choosing an invariant subspace of minimal positive dimension, gives decomposition into irreducibles. The division by $|G|$ uses exactly the characteristic hypothesis.
