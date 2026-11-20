**Strategy.** To prove $x$ is a unit, look for an equation $1=qx$. Divide $1$ by $x$ and use the minimum norm to rule out a remainder.

**Find the inverse.** For $x\ne0$ with $N(x)=m$, @[Euclidean division]mt4-euclidean-domain gives $1=qx+r$. If $r\ne0$, then $N(r)<N(x)=m$, contradicting the choice of $m$ as the minimum over *all* nonzero elements. Thus $r=0$. Since the ring is commutative, $qx=xq=1$, so $q$ is the inverse and $x$ is a @[unit]mt4-unit.

**Apply this to norm zero.** A @[norm]mt4-euclidean-norm takes nonnegative values. If a nonzero element has norm $0$, it attains the minimum and is therefore a unit.
