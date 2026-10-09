**The coset action.** If $aH=bH$, multiplying both cosets by $g$ gives $gaH=gbH$, so $g\cdot(aH)=gaH$ is well defined. Identity and associativity give the action laws. An element $k$ fixes every left coset exactly when $kgH=gH$ for every $g$, equivalently $g^{-1}kg\in H$ for every $g$, or $k\in\bigcap_ggHg^{-1}$. This is the kernel, and taking $g=1$ shows it lies in $H$.

**Cayley.** For $H=1$, the kernel is contained in $1$ and is therefore trivial. The First Isomorphism Theorem identifies $G$ with the image, a subgroup of the symmetric group on its underlying set.

**Smallest-prime index.** If $[G:H]=p$, the coset image lies in $S_p$. Write $K=\ker\rho\le H$ and $k=[H:K]$. The image order is $[G:K]=pk$ by index multiplicativity, and divides $p!$, so $k$ divides $(p-1)!$. Also $k$ divides $|G|$, since it divides $|H|$. Any prime divisor of $k$ would thus be at least $p$ by minimality of $p$, while any prime divisor of $(p-1)!$ is smaller than $p$. This is impossible. Therefore $k=1$, so $H=K$ and $H$ is normal.

The prime being the smallest matters. A maximal subgroup with composite index need not be normal, and an arbitrary prime-index subgroup need not be normal either.
