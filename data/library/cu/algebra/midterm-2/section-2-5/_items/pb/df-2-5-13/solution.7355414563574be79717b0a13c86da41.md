**Step 1: the three maximal subgroups.** Write

$$
A=\langle x,y^2\rangle,\quad B=\langle y\rangle,\quad C=\langle xy\rangle.
$$

They all have order $8$. The group $A$ is $C_2\times C_4$, so the preceding exercise gives its complete lattice after substituting $a=x,b=y^2$.

**Step 2: all order-4 and order-2 subgroups.** The order-$4$ subgroups of $A$ are

$$
D=\langle x,y^4\rangle,\quad E=\langle y^2\rangle,\quad F=\langle xy^2\rangle.
$$

The order-$2$ subgroups are

$$
X=\langle x\rangle,\quad Y=\langle y^4\rangle,\quad Z=\langle xy^4\rangle.
$$

The cyclic group $B$ has the chain $1<Y<E<B$. Also $(xy)^2=y^2$, so $C$ has the chain $1<Y<E<C$. These add no vertices below order $8$ beyond those already inside $A$.

**The complete diagram** is below. The cover relations are: $G$ covers $A,B,C$; $A$ covers $D,E,F$; $B,C$ cover $E$; $D$ covers $X,Y,Z$; $E,F$ cover $Y$; $X,Y,Z$ cover $1$. There are eleven subgroups.

**Step 3: completeness.** Every proper subgroup is contained in $A,B$, or $C$ by the supplied hypothesis. We have exhausted the lattice of $A$ and both cyclic chains. Taking their union therefore gives every subgroup of $G$.

![Complete subgroup lattice for 2.5.13 — Subgroup lattice of C₂ × C₈](/media/486cca2d3d843ee688aeee8f6efb357336e9d992fd62737db7259cee9652d14a.png#width=100&invert=lightness)

**Technique:** build the lattice from maximal subgroups and identify shared subgroups before drawing separate branches.

**Foundations:** @cu:algebra:midterm-2:definitions:df:subgroup-lattice, @cu:algebra:midterm-2:theorems:th:cosets-lagrange.
