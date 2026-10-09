Let $x\in D_{2n}$, $x\neq 1$.  Then
$$
x = s^a r^b.
$$
for some $a\in\set{0,1}$ and $b\in\set{0,1,\ldots, n-1}$

If $a=0$ then $x=r^b$, but $r^b$ does not commute with $s$.

If $b=0$ then $x=s$ but $s$ does not commute with $r$.

So we have $a\neq 0$ and $b\neq 0$.  Now,
$$
sx = s^{a+1} r^b.
$$
but
$$
xs = s^a r^b s = s^{a+1} r^{-b}.
$$

So $sx = xs$ iff $r^b = r^{-b}$.

Suppose $r^b = r^{-b}$.  Then $r^{2b}=1$.  Then, $|r|=n$ divides $2b$.  But because $n$ is odd, $n$ must divide $b$.  But $b\in \set{0, \ldots , n-1}$ and $n$ does not divide $b$.  Therefore $r^b \neq r^{-b}$.


**Remark**: Suppose $n$ was even. There exists an $m\in \Z$ so that $n=2m$.  Then we can have that $m$ divides $b$.  So $m\le b$.  However, if $b<m$, then $r^{2b}\neq 1$ because $2b<n$.  Therefore $b\le m$ and $m=b$.
