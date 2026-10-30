**Start with the requested conclusion.** “Not simple” needs one proper nontrivial normal subgroup (often a kernel). “Solvable” needs a derived-series or extension argument. “Nilpotent” needs a central-series argument or, for finite groups, normal Sylow subgroups. “Classify” needs an exhaustive list **and** proof that the listed groups are distinct.

### A. Given an order: choose the cheapest obstruction first

**1. Few divisors: use the Sylow sieve.** Factor the order and list $n_p\mid|G|/|P|$, $n_p\equiv1\pmod p$. If only1 survives, stop: the Sylow subgroup is normal. In a simplicity contradiction assume $n_p>1$. See @[Sylow theorem]mt3-sylow and @[HW1 4.5.14]mt3-hw1-df-4-5-14.

**2. Prime-order Sylows consume most elements: count.** Distinct order-$p$ subgroups contribute disjoint sets of $p-1$ nonidentity elements. If the removed elements all have order prime to $q$ and precisely $q^a$ elements remain, every Sylow $q$-subgroup must equal that remainder, so it is unique. Do not count larger Sylow subgroups as disjoint without proof. See @[counting warning]mt3-sylow, @[order351]mt3-hw1-df-4-5-15, and @[orders80 and3875]mt3-hw3-df-6-2-4.

**3. Small Sylow number or small subgroup index: act.** A nontrivial action of a hypothetical simple group on $m$ points is faithful; test $|G|\mid m!$, and for nonabelian simple groups the stronger $|G|\mid m!/2$. A prime factor or prime exponent absent from $m!$ gives an immediate contradiction. See @[coset and Sylow actions]mt3-actions and @[HW3 6.2.6]mt3-hw3-df-6-2-6. Small action degree is often faster than element counting.

**4. $n_p$ fails the congruence modulo $p^2$: use the professor's corollary.** Write the failed congruence first. Then choose distinct Sylow $P,Q$ with $H=P\cap Q$ of index $p$ in both. This gives $P,Q\le N_G(H)$; now use the divisors of $|G|$ to determine the normalizer or its possible indices. See @[the exact corollary and proof]mt3-intersection and @[order96 practice]mt3-mock-two. If $|P|=p$, the intersection is trivial and supplies no proper nontrivial normal subgroup.

**5. The $p^2$ test fails: change method.** For $n_2=5$ or $n_3=10$, the corollary cannot force index-$p$ intersections because these are $1$ modulo4 or9. Count, use a small action, or try the generalized $(N)^+$ test modulo $p^k$. An index $p^j$ with $j>1$ does not itself imply normality. See @[limits and alternatives]mt3-nplus-drills and @[the order90 argument]mt3-hw3-extra-simple-61-100.

**6. Two large Sylows overlap: maximize the intersection.** Choose $H=P\cap Q$ with maximum order. The strict normalizer property in $p$-groups then shows $N_G(H)$ is not a $p$-group. Combine the forced factor $p|H|$ and an additional prime factor with Lagrange. Use this when mere overlap does not make $H$ normal. See @[maximal-intersection theorem]mt3-max-intersection and @[HW3 6.2.22]mt3-hw3-df-6-2-22.

**7. A Sylow normalizer has a manageable order: work inside it.** Put $M=N_G(P)$. If another Sylow subgroup $Q$ is unique in $M$, then $M\le N_G(Q)$; compare their orders. Once $Q\trianglelefteq M$ is established, the conjugation map $M\to\Aut(Q)$ can force centralization. Without that normality, restrict to $N_M(Q)$ before using this map. Another route is to enlarge a normalizer using an abelian Sylow subgroup. See @[normalizer-centralizer theorem]mt3-foundations, @[HW3 6.2.10]mt3-hw3-df-6-2-10, and @[HW3 6.2.12]mt3-hw3-df-6-2-12.

### B. Structure, actions, and generators

**8. Normal factor with a candidate complement: use semidirect recognition.** Verify normality, trivial intersection, and full product. Then determine the action into $\Aut(N)$. A quotient isomorphism alone does not prove a splitting. To classify, reduce actions under changes of basis/generators and distinguish the survivors by centers, element orders, or normal subgroups. See @[semidirect definitions]mt3-semidirect, @[classification template]mt3-classify, and @[all groups of order147]mt3-hw1-df-5-5-10.

**9. A $p$-group acts on a finite set whose size is prime to $p$: force a fixed point.** Find the right set: often a set of Sylow subgroups or a coset. For an automorphism action, a fixed subgroup means setwise preservation. In a semidirect product with maximal complement, any nontrivial invariant subgroup immediately gives the whole normal factor. See @[fixed-point congruence]mt3-actions, @[maximal-complement extra]mt3-hw1-extra-maximal-complement, and @[fixed cosets in 6.1.26]mt3-hw2-df-6-1-26.

**10. Nilpotence or solvability: choose the matching series.** Use the lower central series for subgroup/quotient closure and commutator relations; use the upper central series when centers of quotients are easy. For solvability, either compute the derived series or find a solvable normal subgroup and solvable quotient. The extension argument works for solvability, not nilpotence. See @[the three definitions]mt3-series, @[nilpotence criteria]mt3-nilpotent, @[solvable extensions]mt3-solvable, and @[HW2 6.1.7]mt3-hw2-df-6-1-7.

**11. A minimal normal subgroup in a finite solvable group: use characteristic subgroups.** Test $M'$, then the Sylow components of abelian $M$, then $M^p$. Each is characteristic in $M$, hence normal in $G$, so minimality forces1 or $M$. Use solvability, finiteness, or Cauchy to rule out the wrong option. See @[characteristic-in-normal]mt3-foundations and @[HW2 6.1.31]mt3-hw2-df-6-1-31.

**12. In a finite group, a normal subgroup with a Sylow subgroup: try Frattini's argument.** Adjust a conjugator by an element of the normal subgroup to get $G=N N_G(P)$. For the coprime-kernel situation of §6.1.20 ($P$ a $p$-subgroup and $N\trianglelefteq G$ with $p\nmid|N|$), take the quotient normalizer's full inverse image and apply Frattini there to $PN$. For the quotient centralizer, first obtain a normalizing representative, then put its commutator in $P\cap N=1$. These lifting recipes require the coprimality hypothesis. See @[Frattini's argument]mt3-frattini-argument and @[HW2 6.1.20]mt3-hw2-df-6-1-20.

**13. Generators of a finite $p$-group: pass to its Frattini quotient.** $P/\Phi(P)$ turns the question into linear algebra; basis lifts generate and minimal generating sets correspond to bases. To prove $\Phi(G)$ nilpotent for finite $G$, apply Frattini's argument to its Sylow subgroups and use the definition as an intersection of maximal subgroups. See @[Frattini and basis theorem]mt3-frattini and @[HW2 6.1.25]mt3-hw2-df-6-1-25.

**14. Finite abelian invariants: use powers, decomposition, or duality.** For $p$th powers and $p$-torsion, kernel–image counting gives equal dimensions; for subgroup counts, compare lines and hyperplanes. For characters, split into cyclic factors and choose roots of unity. See @[abelian tools]mt3-abelian and @[HW2 5.2.8]mt3-hw2-df-5-2-8 / @[5.2.14]mt3-hw2-df-5-2-14.

**15. A universal property or generator assignment: factor a free map.** Specify generator images, extend freely, show relations lie in the kernel, factor, then prove uniqueness on generators. For an automorphism, still prove injectivity/surjectivity after checking relations. See @[presentations and free objects]mt3-free and @[HW3 6.3.10]mt3-hw3-df-6-3-10 / @[6.3.12]mt3-hw3-df-6-3-12.

### Ten-second choice check

Before writing a proof, finish these sentences: **“My target conclusion is …; the useful object is …; the theorem applies because …; its output gives ….”** If you cannot name the object (action set, normal subgroup, quotient, intersection, or automorphism group), more arithmetic is unlikely to fix the missing strategy.
