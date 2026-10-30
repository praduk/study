$\F_p=\Z/p\Z$ is the field of residues modulo the prime $p$. A vector space over it is an abelian group written additively with scalar multiplication satisfying the distributive and associative laws. A **basis** is a linearly independent spanning set; its size is the dimension. An $r$-dimensional space has $p^r$ vectors. A **line** is a one-dimensional subspace and a **hyperplane** has codimension1 (dimension $r-1$).

A **linear map** preserves addition and scalar multiplication. A **linear functional** maps to $\F_p$. Its kernel is a hyperplane when the functional is nonzero. Every hyperplane arises this way; the nonzero functionals with a given kernel differ by a nonzero scalar.

An elementary abelian $p$-group is an abelian group with $x^p=1$ for every $x$. It is a vector space over $\F_p$: group multiplication plays the role of addition, and powers play the role of scalar multiplication. In finite dimension $r$, it is $C_p^r$.

$\GL_r(\F_p)$ is the group of invertible $r\times r$ matrices over $\F_p$; it is $\Aut(C_p^r)$ after choosing a basis. Its order is

$$
|\GL_r(\F_p)|=(p^r-1)(p^r-p)\cdots(p^r-p^{r-1}),
$$

since successive columns must avoid the span of their predecessors. A **fixed subspace** of a matrix $T$ is $\{v:T v=v\}$. A subspace is **invariant** when $T$ sends it to itself; invariant does not mean fixed pointwise. A diagonal matrix $\diag{u,v}$ multiplies the two coordinates by $u,v$ respectively; a scalar matrix $uI$ preserves every line.

Changing a basis conjugates an action matrix. This is why conjugate actions give isomorphic semidirect products. In the group language, order-$p$ subgroups **contained in the normal base** $C_p^2$ are normal in $C_p^2\semid H$ exactly when their corresponding lines are preserved by the acting group $H$.
