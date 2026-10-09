Let $r(x_1,\ldots,x_p)=(x_2,\ldots,x_p,x_1)$.

**(a) Count by free coordinates.** Choose $x_1,\ldots,x_{p-1}$ arbitrarily. There is exactly one possible last coordinate,

$$
x_p=(x_1\cdots x_{p-1})^{-1},
$$

which makes the product $1$. This gives a bijection $G^{p-1}\to S$ and hence $|S|=|G|^{p-1}$. Since a prime is at least $2$, $p-1\ge1$, and $p\mid |G|$ implies $p\mid|S|$.

**(b) Preserve the product in the noncommutative case.** If $x_1\cdots x_p=1$, then

$$
x_2\cdots x_px_1=x_1^{-1}(x_1\cdots x_p)x_1=1.
$$

So $r(S)\subseteq S$. Repeating this proves every cyclic rotation lies in $S$. We did not commute any of the factors.

**(c) Verify the equivalence relation.** The relation says $\beta=r^j\alpha$ for an integer $j$. Taking $j=0$ proves reflexivity. If $\beta=r^j\alpha$, then $\alpha=r^{-j}\beta$, proving symmetry; negative powers are legitimate because $r^p=\id$. If also $\gamma=r^\ell\beta$, then $\gamma=r^{\ell+j}\alpha$, proving transitivity.

**(d) Characterize singleton classes.** A singleton class means $r\alpha=\alpha$. Coordinate comparison gives $x_1=x_2=\cdots=x_p=x$. Membership in $S$ then says $x^p=1$. Conversely such a constant tuple is unchanged by all rotations and belongs to $S$, so its class is a singleton.

**(e) Explain why no intermediate sizes occur.** The group $C_p=\langle r\rangle$ acts on $S$. By orbit–stabilizer, the size of a class is the index of its stabilizer in $C_p$ and therefore divides $p$. Since $p$ is prime, that positive size is $1$ or $p$. One may also argue directly: if a nonzero rotation $r^j$ fixes a tuple, $1\le j<p$, then $j$ has a multiplicative inverse modulo $p$, so a power of $r^j$ is $r$ and $r$ fixes the tuple. Hence any nonsingleton has all $p$ distinct rotations. Counting the partition into classes gives $|G|^{p-1}=k+pd$.

**(f) Find an element of order p.** Part (a) and the equation in (e) imply $p\mid k$. The tuple $(1,\ldots,1)$ provides one singleton, so $k\ge1$. A positive multiple of $p$ is at least $p$, thus $k\ge p>1$. There must be another singleton $(x,\ldots,x)$ with $x\ne1$ and $x^p=1$. The order of $x$ divides $p$, and cannot be $1$, so it is $p$.

**Technique:** count a finite set modulo $p$ in two ways. Prime-order symmetry isolates fixed points. The rotation calculation is the step where an unjustified commutativity assumption most often sneaks in.

**Foundations:** @cu:algebra:midterm-2:theorems:th:cosets-lagrange, @cu:algebra:midterm-2:theorems:th:first-isomorphism, @cu:algebra:midterm-2:theorems:th:orbit-stabilizer.
