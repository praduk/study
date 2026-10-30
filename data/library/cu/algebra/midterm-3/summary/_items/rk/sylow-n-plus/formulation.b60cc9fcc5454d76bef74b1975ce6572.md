Techniques:

Suppose you are given $n_p$ and are trying to prove $G$ is not simple.  By way of contradiction assume $G$ is simple.

We could look at the action of $G$ on its Sylow-$p$ subgroups by conjugation.  This gives a homomorphism
$$
\phi: G \to S_{n_p}.
$$

Because $G$ is simple, $\ker\phi = 1$ or $\ker\phi = G$.  If $\ker\phi = G$ the action is trivial, but the action is not trivial because Sylow-p subgroups are conjugate and the action is transitive.  So $\ker\phi = 1$ and $\phi$ injective.  Let $\sigma$ be the sign homomorphism.  Then

$$
\sigma \circ \phi : G \to \set{-1, 1}.
$$

The kernel of this map is either trivial or all of $G$.  It usually isn't trivial because $G$ can't embed into a set of size 2, therefore the kernel is everything and $G$ embeds into $A_n$.

At this point if $|G|$ does not divide $|A_n|$ then we're done.

Now suppose there exists a candidate $n_p$ and $n_p \neq 1 \mod p^2$.  Recall @mt3-nplus.  Because $p^2 \nmid 1 \mod p^k$, there exist distinct $P,Q\in \Syl_p(G)$ so that $p^2 \nmid [P:P\cap Q]$.  But then $[P:P\cap Q]\neq p^k$ for $k\ge 2$ and because $[P:P\cap Q]\neq 1$ because $P$ is distinct from $Q$, $[P:P\cap Q]=p$.  $P\cap Q$ is normal in $P$ and $Q$ because it has index $p$ which is the smallest prime dividing the order of the group.

Then look at what groups $H=N_G(P\cap Q)$ could be bigger than $P$ or $Q$ as given by Lagrange.  Then for each one look at the action of $G$ on $G/H$.  Lets say $|G/H|=n$.  Then we have an action of $G$ on $G/H$ (and using the sign homomorphism again) from
$$
G\to A_n.
$$
The kernel is either trivial or all of $G$.  We find that this action is not trivial, and so $G$ embeds into $A_n$.  Show that it can't to get a contradiction.
