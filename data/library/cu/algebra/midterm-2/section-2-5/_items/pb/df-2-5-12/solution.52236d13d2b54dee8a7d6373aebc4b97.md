Subgroups of a cyclic group correspond to divisors.

# Test heading
## Test heading 2

**Step 1: locate the subgroups of order 2.** Every element is uniquely $a^i b^j$ with $i\in\{0,1\}$ and $0\le j<4$. Since $(a^i b^j)^2=b^{2j}$, an element has order dividing $2$ precisely when $j$ is even. The three nonidentity involutions are $a,b^2,ab^2$. Thus the order-$2$ subgroups are

$$
X=\langle a\rangle,\qquad Y=\langle b^2\rangle,\qquad Z=\langle ab^2\rangle.
$$

Each has exactly one nonidentity element, so these subgroups are distinct.

**Step 2: determine the containment edges.** Put $V=\langle a,b^2\rangle$, $B=\langle b\rangle$, and $D=\langle ab\rangle$. The subgroup $V$ contains $X,Y,Z$. The cyclic group $B$ has the unique subgroup $Y$ of order $2$. Since $(ab)^2=b^2$, the cyclic group $D$ also has unique order-$2$ subgroup $Y$.

**The complete Hasse diagram** is given below. Higher vertices are larger subgroups, and each line is a cover relation. There are eight vertices in total. Its edge list, useful for checking the drawing, is: $A$ covers $V,B,D$; $V$ covers $X,Y,Z$; $B,D$ each cover $Y$; and $X,Y,Z$ each cover $1$.

**Step 3: completeness.** By Lagrange, a proper subgroup has order $1,2$, or $4$. We found every subgroup of order $2$ by listing all involutions. The three order-$4$ subgroups and the fact that they contain every proper subgroup are supplied in the problem; their own subgroups have now all been listed. Nothing is missing.

![Complete subgroup lattice for 2.5.12 — Subgroup lattice of C₂ × C₄](/media/5f96f3c7c5bea64d2746bf4565750c89f1a887159fc8e101ac015d4778dc0e13.png#width=100&invert=lightness)

**Technique:** list element orders, then record covers rather than every transitive inclusion. A lattice specifies containments; the fact that two cyclic subgroups share an involution is essential to its shape.

**Foundations:** @cu:algebra:midterm-2:definitions:df:subgroup-lattice, @cu:algebra:midterm-2:theorems:th:cosets-lagrange.
