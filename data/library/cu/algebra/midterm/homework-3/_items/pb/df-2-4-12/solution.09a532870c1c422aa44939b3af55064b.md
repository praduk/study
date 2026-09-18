An invertible upper triangular matrix has nonzero diagonal entries, which over $\F_2$ must all be $1$. Thus the group is exactly the eight matrices $X(a,b,c)$ from the Heisenberg notation, with $a,b,c\in\F_2$.
Let $r=X(1,0,1)$ and $s=X(1,0,0)$. The multiplication rule gives

$$
r^2=X(0,1,0),\quad r^3=X(1,1,1),\quad r^4=I,\quad s^2=I,\quad srs=r^3.
$$

Thus $r$ has order four and the dihedral relations hold. Moreover $s$ is not one of $I,r,r^2,r^3$, so the four elements of $\langle r\rangle$ and the four distinct elements of $s\langle r\rangle$ exhaust the eight matrices. Consequently $r,s$ generate and the homomorphism from the eight-element group $D_8$ onto this group is bijective.

**Technique:** count free coordinates, choose generators with the right orders, check relations, and use cardinality for injectivity.
