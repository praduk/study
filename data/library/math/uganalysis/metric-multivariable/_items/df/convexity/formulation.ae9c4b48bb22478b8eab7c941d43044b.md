A subset $C$ of a real @[vector space]math:algebra:linear-foundations:df:vector-space is convex when $(1-t)x+ty\in C$ for every $x,y\in C$ and $0\le t\le1$. This is also the convention for a complex vector space regarded as a real space. Empty sets and singletons are convex.

A real-valued function $f:C\to\R$ on a convex domain is convex when

$$
f((1-t)x+ty)\le(1-t)f(x)+tf(y)
$$

for all $x,y\in C$ and $0\le t\le1$. It is strictly convex when the inequality is strict for $x\ne y$ and $0<t<1$. It is concave when $-f$ is convex. Affine functions obey equality; strict convexity is a stronger condition than convexity.

On $\R$, $x\mapsto x^2$ is strictly convex because the difference between the right and left sides is $t(1-t)(x-y)^2$. The set $\{-1,1\}$ is not convex because it omits its midpoint. Convexity depends on the stated affine structure; it is not invariant under arbitrary nonlinear changes of coordinates.
