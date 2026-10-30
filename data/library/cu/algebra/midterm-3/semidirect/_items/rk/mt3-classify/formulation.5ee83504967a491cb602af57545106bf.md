**Proof template.** (1) Force a normal Sylow factor. (2) Find a complement. (3) List the possible factor groups. (4) List homomorphisms into the normal factor's automorphism group. (5) Identify actions related by changes of generators. (6) Distinguish the resulting groups by an invariant.

For $p<q$ and $|G|=pq$, the Sylow $q$-subgroup is normal, so $G=C_q\semid C_p$. If $p\nmid q-1$, only the cyclic group occurs. If $p\mid q-1$, there is one additional nonabelian isomorphism type: the nontrivial maps into the unique order-$p$ subgroup of $\Aut(C_q)$ become equivalent when the generator of $C_p$ changes.

For $N=C_q$ and a complement of order4, check **both $C_4$ and $C_2\times C_2$**. Possible image orders divide both4 and $q-1$. For a $C_4$ complement, trivial, order2, and order4 actions need separate attention; the last exists only if $4\mid q-1$. For a $C_2^2$ complement, its image in a cyclic automorphism group has order at most2.

Useful invariants: abelian/nonabelian; element orders; number of involutions; $Z(G)$; $G'$; and quotients by characteristic subgroups. Different action formulas do **not** automatically mean nonisomorphic groups.

**Center-complement extra:** a splitting over $Z(G)$ has trivial action, so it is a direct product. A nontrivial finite $p$-group complement has nontrivial center, contradicting that its intersection with $Z(G)$ is1.

**Maximal-complement extra:** find a $P$-invariant Sylow subgroup $Q\le G$ by a fixed-point action on $\Syl_q(G)$. Then $P<Q\semid P\le G\semid P$ and maximality forces $Q=G$. Now $Z(G)$ is nontrivial and characteristic; repeat with $Z(G)\semid P$ to force $G=Z(G)$. The prime $q$ is not assumed different from $p$.
