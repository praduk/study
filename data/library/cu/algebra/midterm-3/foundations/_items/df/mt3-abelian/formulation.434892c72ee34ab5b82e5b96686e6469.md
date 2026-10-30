Every finite abelian group is a direct product of cyclic prime-power groups. Equivalently it has a unique invariant-factor description

$$
A\cong C_{n_1}\times\cdots\times C_{n_t},\qquad n_{i+1}\mid n_i,\quad n_i>1,
$$

using Dummit–Foote's decreasing divisibility convention. For coprime $m,n$, $C_m\times C_n\cong C_{mn}$. To distinguish finite abelian $p$-groups, count elements killed by $p^k$: in $\prod_i C_{p^{a_i}}$ that number is $p^{\sum_i\min(k,a_i)}$.

For abelian $A$, $x\mapsto x^n$ is a homomorphism, with kernel $A[n]=\{x:x^n=1\}$ and image $A^n$. For finite $A$, $|A/A^n|=|A[n]|$. In a nonabelian group the power map need not be a homomorphism.

A **complex linear character** of $A$ is a homomorphism $\chi:A\to\C^\times$. The **character group** $\widehat A=\Hom(A,\C^\times)$ uses pointwise multiplication. A character of $C_n=\langle a\rangle$ is determined by $\chi(a)=e^{2\pi i k/n}$, $k\in\Z/n\Z$, so $\widehat{C_n}\cong C_n$.

For finite products, $\widehat{A\times B}\cong\widehat A\times\widehat B$: restrict a character to the factors, and recover it by $\chi(a,b)=\chi_A(a)\chi_B(b)$. Hence finite abelian $A$ is isomorphic to $\widehat A$. This isomorphism requires choices; the evaluation map into the double dual is canonical.

Prerequisites for HW2 §5.2.8,14 and §6.1.26 are now in place. The homework gives the precise assigned applications, including all subparts.
