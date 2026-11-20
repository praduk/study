**Strategy.** Prove both directions. If the ideals agree, write each generator as a multiple of the other and use cancellation to find a unit. For the converse, use the unit and its inverse to prove the two ideal inclusions.

**Equal ideals give a unit multiplier.** By @[the description of principal ideals]mt4-principal-ideal, $(a)=(b)$ gives $a=rb$ and $b=sa$ for some $r,s\in R$. If $a=0$, then $b=sa=0$ and the unit $1$ works. If $a\ne0$, substitution gives $a=(rs)a$. In an @[integral domain]mt4-integral-domain we can @[cancel]mt4-cancellation the nonzero factor $a$, giving $1=rs$. Commutativity gives $sr=1$ as well. Thus $r$ is a @[unit]mt4-unit and $a=rb$.

**A unit multiplier gives equal ideals.** Suppose $a=ub$ for a unit $u$. Every multiple of $a$ is a multiple of $b$, so $(a)\subseteq(b)$. Since $b=u^{-1}a$, every multiple of $b$ is also a multiple of $a$. The two inclusions give $(a)=(b)$.
