**Step 1: a useful conjugation rule.** The relation $vu=uv^5$ gives $uvu=v^5$ because $u^2=1$. Thus

$$
uv^j u=v^{5j}
$$

for every integer $j$. In particular $uv^2u=v^{10}=v^2$, so $u$ commutes with $v^2$.

**Step 2: identify the maximal subgroups.** The commuting generators $u$ and $v^2$ have orders $2$ and $4$. Their cyclic subgroups intersect trivially: if $u$ belonged to $\langle v\rangle$, then $u,v$ would generate a group of at most order $8$, contrary to $|M|=16$. Consequently the eight products $u^i v^{2j}$ are distinct, and $(i,j)\mapsto u^i v^{2j}$ identifies $\langle u,v^2\rangle$ with $C_2\times C_4$. The subgroup $\langle v\rangle$ is $C_8$ by the given order and the presentation. For the third subgroup,

$$
(uv)^2=u(vu)v=u(uv^5)v=v^6.
$$

Since $v^6$ has order $4$, $uv$ has order $8$: its eighth power is $1$, while its fourth power is $v^{12}=v^4\ne1$. Thus $\langle uv\rangle\cong C_8$.

**Step 3: glue the lattices.** In $\langle u,v^2\rangle$ the order-$4$ subgroups are $\langle u,v^4\rangle,\langle v^2\rangle,\langle uv^2\rangle$ and the order-$2$ subgroups are $\langle u\rangle,\langle v^4\rangle,\langle uv^4\rangle$. Both cyclic maximal subgroups contain the chain

$$
1<\langle v^4\rangle<\langle v^2\rangle,
$$

because $\langle(uv)^2\rangle=\langle v^6\rangle=\langle v^2\rangle$. The problem says every proper subgroup is in a maximal subgroup on this list, so the list is complete. Substituting $x\mapsto u,y\mapsto v$ in the vertex labels of Exercise 13 preserves every cover relation. This is a lattice isomorphism, not a group homomorphism.

**Step 4: distinguish the groups.** The elements $u,v$ do not commute: if $vu=uv$, comparison with $vu=uv^5$ would imply $v=v^5$ and hence $v^4=1$, contradicting $|v|=8$. Thus $M$ is nonabelian whereas $C_2\times C_8$ is abelian. They cannot be isomorphic.

![Complete subgroup lattice for 2.5.14 — Same lattice, different groups](/media/a2a0ddf1f1b0f8884e08ebd0291f3f90a855b0e329a3f9325ecfa6a386bc4e31.png#width=100&invert=lightness)

**Technique:** a subgroup lattice records inclusion, but it does not determine multiplication.

**Foundations:** @cu:algebra:midterm-2:definitions:df:subgroup-lattice, @cu:algebra:midterm-2:theorems:th:cosets-lagrange.
