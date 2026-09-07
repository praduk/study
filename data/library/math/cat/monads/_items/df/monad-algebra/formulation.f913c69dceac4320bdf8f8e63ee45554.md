For a monad $(T,\eta,\mu)$, a T-algebra is an object $A$ with a map $a:TA\to A$ satisfying

$$
a\eta_A=\id_A,\qquad aT(a)=a\mu_A.
$$

A morphism from $(A,a)$ to $(B,b)$ is $f:A\to B$ with $fa=bT(f)$. These form a category by functoriality.

For the finite-list monad, a monoid defines such an algebra by multiplying a finite list in order and sending the empty list to its identity. The algebra axioms encode the unit and associativity laws. This example suggests the relation between monads and algebraic structure; no general monadicity theorem is asserted here.
