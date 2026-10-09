Put $s=(1\ 3)$ and $r=(1\ 2\ 3\ 4)$. Then $s^2=1$, $r^4=1$, and conjugating $r$ by $s$ gives

$$
srs=(3\ 2\ 1\ 4)=(1\ 4\ 3\ 2)=r^{-1}.
$$

Using $sr=r^{-1}s$, every word in $r,s$ can be rewritten as $r^i$ or $sr^i$, with $0\le i<4$. Thus the generated group has at most eight elements.

The four powers of $r$ are distinct because $r$ has order $4$. Also $s\notin\langle r\rangle$: the nonidentity powers of $r$ are two $4$-cycles and the double transposition $(1\ 3)(2\ 4)$, none of which is $s$. Hence the four elements $sr^i$ are distinct from the powers of $r$ and from one another. There are exactly eight elements.

The standard dihedral presentation maps onto this group by sending its rotation and reflection to $r,s$. Both groups have order $8$, so the map is an isomorphism. Thus the subgroup is $D_8$. Since $|S_4|=24$, it is proper.

**Technique:** relations give an upper bound by normal forms; distinguish the normal forms to obtain the matching lower bound.

**Foundations:** @cu:algebra:midterm-2:proof-techniques:rk:permutation-method, @cu:algebra:midterm-2:definitions:df:simple-composition.
