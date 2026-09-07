An injective function cancels on the left by evaluating at each element. If $f:A\to B$ is not injective, choose distinct $a,a'$ with $f(a)=f(a')$. The maps from a one-element set selecting $a$ and $a'$ violate monicity.

A surjective function cancels on the right because each element of $B$ has a preimage. If $f$ is not surjective, choose $b\in B\setminus f(A)$. Let $u:B\to\{0,1\}$ be constant zero, and let $v$ be $1$ at $b$ and zero elsewhere. Then $uf=vf$ but $u\ne v$, so $f$ is not epic. This reasoning includes empty sets.
