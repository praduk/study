**Definitions and results used:** @[Center]cu:algebra:midterm-3:foundations:df:mt3-center; @[Quotient groups]cu:algebra:midterm-3:foundations:df:mt3-quotient; @[Commutators]cu:algebra:midterm-3:foundations:df:mt3-series; @[Upper central series]cu:algebra:midterm-3:foundations:df:mt3-upper-central; @[Lower central series]cu:algebra:midterm-3:foundations:df:mt3-lower-central; @[Derived series]cu:algebra:midterm-3:foundations:df:mt3-derived-series; @[Nilpotence and class]cu:algebra:midterm-3:foundations:df:mt3-nilpotent-definition; @[Solvability and derived length]cu:algebra:midterm-3:foundations:df:mt3-solvable-definition; @[Equivalent central-series criteria]cu:algebra:midterm-3:central:th:mt3-central-series-equivalence.

**Technique:** For the upper series, take centers in successive quotients and lift them back to $G$. For the lower series, compute commutators with rotations. For the derived series, take commutators within the current subgroup.

**Working facts.** The relation $sr^k=r^{-k}s$ reduces every element to $r^k$ or $r^ks$, with $0\le k<12$. These $24$ forms are distinct because $|G|=24$. Rotations commute with one another, while every reflection conjugates a rotation to its inverse. With our commutator convention,

$$
[s,r^m]=sr^ms^{-1}r^{-m}=r^{-2m}.
$$

**(a) Upper central series.** A rotation $r^k$ is central exactly when it commutes with $s$, since it already commutes with $r$. This means $r^k=r^{-k}$, or $12\mid2k$. Thus the central rotations are $1$ and $r^6$. No reflection is central: $r^ks$ conjugates $r$ to $r^{-1}\ne r$. Therefore

$$
Z_0(G)=1,\qquad Z_1(G)=Z(G)=\langle r^6\rangle.
$$

Now work in $G/Z_1(G)$, writing $\bar r=rZ_1(G)$ and $\bar s=sZ_1(G)$. This is the dihedral group of order $12$: $\bar r$ has order $6$, and $\bar s$ acts by inversion. The same center calculation, now modulo $6$, gives

$$
Z(G/Z_1(G))=\langle\bar r^3\rangle.
$$

The next upper-central term is its **full inverse image in $G$**, not this quotient subgroup itself:

$$
Z_2(G)=\langle r^3,r^6\rangle=\langle r^3\rangle.
$$

The quotient $G/\langle r^3\rangle$ has order $6$, with a rotation of order $3$ and a reflection acting by inversion. It is $D_6\cong S_3$; one identification sends the rotation to $(123)$ and the reflection to $(12)$. Its center is trivial: a central rotation must satisfy $3\mid2k$, and a reflection does not commute with the order-$3$ rotation. Consequently $Z_3(G)=Z_2(G)$. Repeating the same quotient calculation gives

$$
\boxed{\begin{aligned}Z_0(G)&=1,\\Z_1(G)&=\langle r^6\rangle,\\Z_i(G)&=\langle r^3\rangle\quad(i\ge2).\end{aligned}}
$$

**Lower central series.** First prove both containments for $G'$. The subgroup $\langle r^2\rangle$ is normal because conjugation by $r$ fixes it and conjugation by $s$ inverts it. In $G/\langle r^2\rangle$, the image of $r$ has order $2$, so inversion fixes it; the images of $r$ and $s$ therefore commute. The quotient map sends every commutator to the identity because the quotient is abelian. Every generator of $G'$ therefore lies in its kernel, giving $G'\le\langle r^2\rangle$. Conversely, $[s,r]=r^{-2}$ generates $\langle r^2\rangle$, so

$$
\gamma_2(G)=G'=\langle r^2\rangle.
$$

For any integer $m$, put $H_m=\langle r^m\rangle$. For every integer $t$, rotations commute with $r^{mt}$ and reflections invert it. Hence

$$
[r^k,r^{mt}]=1,\qquad [r^ks,r^{mt}]=r^{-2mt}.
$$

All these commutators lie in $\langle r^{2m}\rangle$, and $[s,r^m]=r^{-2m}$ generates that subgroup. Thus $[G,H_m]=\langle r^{2m}\rangle$. Successive exponents double:

$$
\gamma_2(G)=\langle r^2\rangle,\quad
\gamma_3(G)=\langle r^4\rangle,\quad
\gamma_4(G)=\langle r^8\rangle=\langle r^4\rangle.
$$

The last equality follows from $r^8=(r^4)^2$ and $(r^8)^2=r^{16}=r^4$. The same subgroup therefore persists at every later step:

$$
\boxed{\begin{aligned}\gamma_1(G)&=G,\\\gamma_2(G)&=\langle r^2\rangle,\\\gamma_i(G)&=\langle r^4\rangle\quad(i\ge3).\end{aligned}}
$$

In the lecture's indexing, $L_i(G)=\gamma_{i+1}(G)$: $L_0=G$, $L_1=\langle r^2\rangle$, and $L_i=\langle r^4\rangle$ for $i\ge2$.

**(b) Derived series and conclusions.** We already found $G'=\langle r^2\rangle$, a nontrivial cyclic group of order $6$. It is abelian, so its own commutator subgroup is trivial:

$$
\boxed{\begin{aligned}G^{(0)}&=G,\\G^{(1)}&=\langle r^2\rangle,\\G^{(i)}&=1\quad(i\ge2).\end{aligned}}
$$

Therefore $G$ is **solvable of derived length $2$**. It is **not nilpotent**: the upper series stabilizes at a proper subgroup of order $4$, rather than reaching $G$. Equivalently, the lower series stabilizes at a nontrivial subgroup of order $3$, rather than reaching $1$.

The key distinction is

$$
G''=[G',G']=1,\qquad \gamma_3(G)=[G,G']=\langle r^4\rangle\ne1.
$$

The derived series uses only rotations after its first step, so the next term is trivial. The lower central series continues taking commutators with reflections from the whole group. Stabilizing at the second upper term does **not** mean nilpotency class $2$: that would require $Z_2(G)=G$.
