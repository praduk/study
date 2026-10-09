Let $r(x_1,\ldots,x_p)=(x_2,\ldots,x_p,x_1)$.

**(a) Count by free coordinates.** Choose $x_1,\ldots,x_{p-1}$ arbitrarily. There is exactly one possible last coordinate,

$$
x_p=(x_1\cdots x_{p-1})^{-1},
$$

Therefore $|S|=|G|^{p-1}$.  Because $p \mid |G|^{p-1}$, $p \mid |S|$.

**(b) Preserve the product in the noncommutative case.** If $x_1\cdots x_p=1$, then

$$
x_2\cdots x_px_1=x_1^{-1}(x_1\cdots x_p)x_1=1.
$$

So $r(S)\subseteq S$. Repeating this proves every cyclic rotation lies in $S$.

**(c) Verify the equivalence relation.** The relation says $\beta=r^j\alpha$ for an integer $j$. Taking $j=0$ proves reflexivity. If $\beta=r^j\alpha$, then $\alpha=r^{-j}\beta$, proving symmetry; negative powers are legitimate because $r^p=\id$. If also $\gamma=r^\ell\beta$, then $\gamma=r^{\ell+j}\alpha$, proving transitivity.

**(d) Characterize singleton classes.** A singleton class means $r\alpha=\alpha$. Coordinate comparison gives $x_1=x_2=\cdots=x_p=x$. Membership in $S$ then says $x^p=1$. Conversely such a constant tuple is unchanged by all rotations and belongs to $S$, so its class is a singleton.

**(e) Explain why no intermediate sizes occur.** The group $C_p=\langle r\rangle$ acts on $S$. Let $s\in S$.  By orbit–stabilizer,
$$
|\Orb_{C_p}(s)||\Stab_{C_p}(s)| = |G|.
$$
Because $p \mid |G|$, either $p \mid |\Orb_{C_p}(s)|$ or $p \mid |\Stab_{C_p}(s)|$.  Therefore $|\Orb_{C_p}(s)|\in \set{1,p}$.  Hence,
$$
|G|^{p-1}=k+pd.
$$

**(f) Find an element of order p.** Part (a) and the equation in (e) imply $p\mid k$. The tuple $(1,\ldots,1)$ provides one singleton, so $k\ge1$. A positive multiple of $p$ is at least $p$, thus $k\ge p>1$. There must be another singleton $(x,\ldots,x)$ with $x\ne1$ and $x^p=1$. The order of $x$ divides $p$, and cannot be $1$, so it is $p$.

**Foundations:** @cu:algebra:midterm-2:theorems:th:cosets-lagrange, @cu:algebra:midterm-2:theorems:th:first-isomorphism, @cu:algebra:midterm-2:theorems:th:orbit-stabilizer.
