**Definitions and results used:** @[Simple groups]mt3-simple; @[Group actions and kernels]mt3-group-action; @[The sign homomorphism]mt3-sign-homomorphism; @[Lagrange theorem]mt3-lagrange.

There are $m!$ permutations of $m$ points: successively choose the images in $m,m-1,\ldots,1$ ways. For $m\ge2$, the sign homomorphism is onto $C_2$, so its kernel $A_m$ has half this order.

The kernel of $\rho$ is normal in $G$. Simplicity leaves only $1$ or $G$, and a nontrivial action excludes kernel $G$. Thus $\rho$ is injective, giving the divisibility by $m!$.

Now suppose $G$ is nonabelian. The composite $\sgn\circ\rho:G\to C_2$ also has normal kernel. If it were nontrivial, simplicity would make it injective, forcing $G$ to be isomorphic to a subgroup of the abelian group $C_2$, a contradiction. Its image is therefore trivial, so $\rho(G)\le A_m$. Apply Lagrange again.

Finally a trivial action has singleton orbits and cannot be transitive on a set with more than one point.
