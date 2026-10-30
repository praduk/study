**Definitions and results used:** @[External semidirect product]cu:algebra:midterm-3:semidirect:df:mt3-semidirect; @[Actions of one finite cyclic group on another]cu:algebra:midterm-3:semidirect:th:mt3-cyclic-actions; @[Center of a group]cu:algebra:midterm-3:foundations:df:mt3-center; @[Commutators and commutator subgroups]cu:algebra:midterm-3:foundations:df:mt3-series; @[Upper central series]cu:algebra:midterm-3:foundations:df:mt3-upper-central; @[Lower central series]cu:algebra:midterm-3:foundations:df:mt3-lower-central; @[Derived series]cu:algebra:midterm-3:foundations:df:mt3-derived-series; @[Nilpotent group and nilpotency class]cu:algebra:midterm-3:foundations:df:mt3-nilpotent-definition; @[Solvable group and derived length]cu:algebra:midterm-3:foundations:df:mt3-solvable-definition.

**(a).** The map $a\mapsto a^2$ is an automorphism, and $2^3\equiv1\pmod7$, so its cube is the identity. The semidirect product exists and has order21, with normal factor $\langle a\rangle$. Its multiplication is

$$
(a^ib^j)(a^kb^\ell)=a^{i+2^jk}b^{j+\ell},
$$

where exponents are reduced modulo7 and3 respectively.

**(b).** For $a^ib^j$ to commute with $a$, $2^j\equiv1\pmod7$, so $j=0$. Commuting with $b$ then requires $2i\equiv i\pmod7$, so $i=0$. Thus $Z(G)=1$ and every upper-central term is1.

Since $G/\langle a\rangle$ is cyclic, $G'\le\langle a\rangle$. But $[b,a]=a^2a^{-1}=a$, so $G'=\langle a\rangle$. It follows that $L_0=G$ and $L_i=\langle a\rangle$ for every $i\ge1$, because $[b,a]=a$ keeps the next term nontrivial. The derived series is $G\trianglerighteq\langle a\rangle\trianglerighteq1$. Hence $G$ is not nilpotent, and is solvable of derived length2.

**Check:** a cyclic normal subgroup and cyclic quotient do not imply the whole group is cyclic or nilpotent.
