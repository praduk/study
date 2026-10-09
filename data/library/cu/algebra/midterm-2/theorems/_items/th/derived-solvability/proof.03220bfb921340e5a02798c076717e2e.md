**Solvable series implies derived termination.** Write a solvable series downward as $G=G_0\trianglerighteq G_1\trianglerighteq\cdots\trianglerighteq G_t=1$, each adjacent quotient abelian. The commutator criterion gives $G_i'\le G_{i+1}$. Inductively $G^{(i)}\le G_i$: the base case is equality, and commutators of elements of $G^{(i)}\le G_i$ lie in $G_i'\le G_{i+1}$. Thus $G^{(t)}=1$.

**Derived termination implies a solvable series.** Each $G^{(i+1)}$ is normal in $G^{(i)}$, and the quotient by its commutator subgroup is abelian. Hence the finite derived chain ending at $1$ is a solvable series, read upward. Repeated terms can be omitted.

**Subgroups.** If $H\le G$, then $H^{(i)}\le G^{(i)}$ by induction: it holds initially, and generating commutators preserves inclusion. Termination for $G$ therefore implies termination for $H$.

**Quotients.** A surjective homomorphism $f:G\to Q$ satisfies $f(G')=Q'$, because it sends every commutator to a commutator, and every commutator in $Q$ has preimages in $G$. Induction gives $f(G^{(i)})=Q^{(i)}$. Thus quotients of solvable groups are solvable.

**Extensions.** If $N$ and $G/N$ are solvable, choose $s,t$ with $(G/N)^{(s)}=1$ and $N^{(t)}=1$. Projection then gives $G^{(s)}\le N$. Applying the subgroup-inclusion observation repeatedly yields

$$
G^{(s+t)}=(G^{(s)})^{(t)}\le N^{(t)}=1.
$$

So $G$ is solvable. Conversely, if $G$ is solvable, the subgroup and quotient results already proved apply to $N$ and $G/N$. No finite-order assumption is required.
