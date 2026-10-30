The **free group** $F(S)$ consists of reduced finite words in symbols $s,s^{-1}$ for $s\in S$; multiplication concatenates and cancels adjacent inverse pairs. Its universal property: every set map $S\to G$ extends uniquely to a homomorphism $F(S)\to G$.

A **presentation** $\langle S\mid R\rangle$ means $F(S)/\langle\!\langle R\rangle\!\rangle$, where the double brackets denote normal closure. To define a homomorphism from a presented group, assign generator images and verify **every defining relation**. Relations alone give a homomorphism, not necessarily an isomorphism; prove injectivity or generation plus a suitable finite-order argument.

For $S_n$, adjacent transpositions $t_i=(i\ i+1)$ have the presentation

$$
t_i^2=1,\qquad(t_it_{i+1})^3=1,\qquad[t_i,t_j]=1\quad(|i-j|\ge2).
$$

An **inner automorphism** is conjugation by a group element; an **outer automorphism** is an automorphism not of that form. Conjugation in $S_n$ preserves cycle type. Thus a verified automorphism of $S_6$ sending a transposition to three disjoint transpositions is outer. HW3 §6.3.10 checks the explicit five images.

**Free nilpotent group of class at most $c$:** with $L_0(F)=F$ and $L_{i+1}(F)=[F,L_i(F)]$, the quotient $F(S)/L_c(F(S))$ is universal for maps from $S$ to nilpotent groups of class at most $c$.

**Proof template for the universal property:** extend a map on $S$ freely → show the relevant subgroup lies in the kernel → factor through the quotient → prove uniqueness on generators. Homomorphisms preserve lower-central terms, so $F\to H$ kills $L_c(F)$ whenever $L_c(H)=1$. Be careful about the indexing: with $\gamma_1=F$, the denominator is $\gamma_{c+1}(F)$.

For quotient freeness, distinguish “class at most $c$” (the universal property) from “class exactly $c$” (requires sufficient generators and a separate argument). The rank-one free nilpotent group is cyclic for every $c\ge1$.

**Earlier permutation-group theorem used in §6.3.10:** $A_n$ is simple for $n\ge5$ (Dummit–Foote §4.6, Theorem24), so in particular $A_6$ is simple. This is a previously established theorem, not a consequence of merely checking the displayed relations. Also $Z(S_n)=1$ for $n\ge3$: a central permutation conjugates each $(ij)$ to itself, hence preserves every two-element subset, which forces every point fixed. These are the inputs to the kernel argument for the $S_6$ automorphism.
