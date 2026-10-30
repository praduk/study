**Definitions and results used:** @[finite p-groups are nilpotent]mt3-pgroups; @[finite nilpotent groups are direct products of Sylow subgroups]mt3-nilpotent; @[dihedral relations and commuting normal factors]mt3-foundations.

**Technique:** Test coprime-order commutation using a reflection and an odd-order rotation.

If $n=2^a$, then $|D_{2n}|=2^{a+1}$, so it is a finite $2$-group and is nilpotent.

Conversely, if $n$ has an odd prime divisor $q$, then $a=r^{n/q}$ has order $q$, while $s$ has order $2$. In a finite nilpotent group, elements of relatively prime orders commute: they lie in products of disjoint normal Sylow factors. Here $sas^{-1}=a^{-1}\ne a$, since $a$ has odd order greater than $1$. This contradiction proves that no odd prime divides $n$, so $n$ is a power of $2$.
