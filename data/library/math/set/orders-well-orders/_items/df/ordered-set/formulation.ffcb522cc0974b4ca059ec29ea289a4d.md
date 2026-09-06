A relation $\le$ on $P$ is a **preorder** if it is reflexive and transitive. It is a **partial order** if it is also antisymmetric:

$$
x\le y\land y\le x\to x=y.
$$

It is a **linear order** if every $x,y\in P$ are comparable: $x\le y$ or $y\le x$. The associated strict order is
$x<y$ iff $x\le y$ and $x\ne y$.

An order embedding $f:P\to Q$ is an injection satisfying
$x\le_Py$ iff $f(x)\le_Qf(y)$. An order isomorphism is a surjective order embedding.
