Use the @[definitions of ideal sum and product]mt4-ideal-sum-product and the @[two-sided ideal test]mt4-ideal.

**(a)** Zero lies in $I+J$. Differences split as $(i+j)-(i'+j')=(i-i')+(j-j')$. Left and right multiplication distribute and preserve the respective summands. Thus $I+J$ is an ideal. It contains $I$ and $J$ by taking the other summand zero. Every ideal containing both is closed under their sums, proving minimality.

**(b)** Zero and differences of finite sums of products lie in $IJ$, since $-(ij)=(-i)j$. For $r\in R$, $r(ij)=(ri)j$ and $(ij)r=i(jr)$ are again products of the required form. Distribute over finite sums to get two-sided absorption. Also $ij\in I$ since $I$ is a right ideal, and $ij\in J$ since $J$ is a left ideal. Their finite sums lie in $I\cap J$.

**(c)** In $\Z$ take $I=J=2\Z$. Their intersection contains $2$, while every term in a sum of products of two even integers is divisible by $4$. In fact $IJ=4\Z$, since $4k=(2k)2$.

**(d)** Write $1=i+j$ with $i\in I,\ j\in J$. For $z\in I\cap J$, $z=iz+zj$ by commutativity. Both summands belong to $IJ$, using $z\in J$ in the first and $z\in I$ in the second. Thus $I\cap J\subseteq IJ$, and (b) gives the reverse inclusion.
