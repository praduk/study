**Step 1: show the two factors commute.** For $h\in H,k\in K$, the commutator $h^{-1}k^{-1}hk$ lies in $H$, since $k^{-1}hk\in H$ by normality. It also lies in $K$, since $h^{-1}k^{-1}h\in K$. Thus it is in $H\cap K=1$, giving $hk=kh$.

**Step 2: define the map and check multiplication.** Put $f(h,k)=hk$. Using the commutation just proved,

$$
f((h,k)(h',k'))=hh'kk'=hkh'k'=f(h,k)f(h',k').
$$

So $f$ is a homomorphism. The assumption $G=HK$ is exactly its surjectivity.

**Step 3: prove injectivity.** If $f(h,k)=1$, then $h=k^{-1}$ lies in $H\cap K$, so both $h$ and $k$ are identity. The kernel is trivial, making $f$ injective. Thus it is an isomorphism.

Both normality hypotheses are used in Step 1. If just one factor is normal, a complement may exist without giving a direct product.
