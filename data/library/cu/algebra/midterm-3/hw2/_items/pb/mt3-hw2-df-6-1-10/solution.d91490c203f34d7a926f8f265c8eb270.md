**Definitions and results used:** @[Notation and conventions]cu:algebra:midterm-3:foundations:rk:mt3-notation; @[Finite p-groups are nilpotent]cu:algebra:midterm-3:sylow:th:mt3-pgroup-nilpotent; @[Equivalent criteria for finite nilpotent groups]cu:algebra:midterm-3:central:th:mt3-nilpotent; @[Disjoint normal subgroups commute]cu:algebra:midterm-3:foundations:th:mt3-normal-commute; @[Lagrange’s theorem and the index formula]cu:algebra:midterm-3:foundations:th:mt3-lagrange.

**Technique:** Test coprime-order commutation using a reflection and an odd-order rotation.

If $n=2^a$, then $|D_{2n}|=2^{a+1}$, so it is a finite $2$-group and is nilpotent.

Conversely, if $n$ has an odd prime divisor $q$, then $a=r^{n/q}$ has order $q$, while $s$ has order $2$. In a finite nilpotent group, elements of relatively prime orders commute: they lie in products of disjoint normal Sylow factors. Here $sas^{-1}=a^{-1}\ne a$, since $a$ has odd order greater than $1$. This contradiction proves that no odd prime divides $n$, so $n$ is a power of $2$.
