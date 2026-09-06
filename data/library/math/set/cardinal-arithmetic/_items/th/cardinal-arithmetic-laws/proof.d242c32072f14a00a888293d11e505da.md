Under the ZFC convention of the preceding definition, each law is induced by an explicit bijection. Swapping tags gives
$A\sqcup B\approx B\sqcup A$, while reassociating tags gives
$(A\sqcup B)\sqcup C\approx A\sqcup(B\sqcup C)$. Coordinate swap gives
$A\times B\approx B\times A$, and
$((a,b),c)\mapsto(a,(b,c))$ gives associativity of products.

For distributivity, map

$$
(a,(0,b))\mapsto(0,(a,b)),\qquad
(a,(1,c))\mapsto(1,(a,c)).
$$

This is a bijection from $A\times(B\sqcup C)$ to
$(A\times B)\sqcup(A\times C)$.

A function on the disjoint union $B\sqcup C$ is uniquely a pair consisting of its restrictions to $B$ and $C$, proving
$|A|^{|B|+|C|}=|A|^{|B|}|A|^{|C|}$. Finally, a function
$C\to{}^B A$ is uniquely equivalent, by evaluation and currying, to a function
$B\times C\to A$. This proves
$(|A|^{|B|})^{|C|}=|A|^{|B||C|}$.
