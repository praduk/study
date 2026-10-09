Define

$$
f:G\to(G/M)\times(G/N),\qquad f(g)=(gM,gN).
$$

Normality makes both quotient groups legitimate and gives $f(gh)=(ghM,ghN)=f(g)f(h)$. The kernel is exactly $M\cap N$, since both coordinates are identity cosets precisely when $g$ belongs to both subgroups.

**The point requiring care is surjectivity.** Take arbitrary target cosets $(aM,bN)$. Since $G=MN$, write $a^{-1}b=mn$ with $m\in M,n\in N$. Set $g=am$. Then $gM=aM$ because $m\in M$. Also $b=amn=gn$, so $gN=bN$. Thus every pair of cosets has a preimage.

The First Isomorphism Theorem now gives the stated isomorphism, with induced map $g(M\cap N)\mapsto(gM,gN)$.

The relevant lattice is the diamond with top $G=MN$, middle vertices $M,N$, and bottom $M\cap N$. The lines here express inclusion and need not be covers. The second isomorphism theorem identifies $M/(M\cap N)$ with $G/N$ and $N/(M\cap N)$ with $G/M$.

**Check the assumption.** Without $G=MN$, the map still exists and has the same kernel, but its image need not be the full product. For $M=N=1$ it is the diagonal subgroup of $G\times G$.

![Inclusion diamond with G=MN above M and N above their intersection](/media/79418aea22de5ff10603f3663da5003131e031948402ef450552d43882ed7603.png#width=100&invert=lightness)

**Technique:** use a single map to the product. Identify its kernel and prove joint surjectivity rather than just surjectivity of each coordinate.

**Foundations:** @cu:algebra:midterm-2:theorems:th:first-isomorphism, @cu:algebra:midterm-2:theorems:th:second-isomorphism, @cu:algebra:midterm-2:theorems:th:correspondence, @cu:algebra:midterm-2:theorems:th:product-order.
