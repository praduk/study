A monad on a category $\mathcal C$ is an endofunctor $T:\mathcal C\to\mathcal C$ with natural transformations $\eta:\id\Rightarrow T$ and $\mu:T^2\Rightarrow T$ satisfying, at every object $A$,

$$
\mu_A T(\eta_A)=\id_{TA}=\mu_A\eta_{TA},\qquad\mu_A T(\mu_A)=\mu_A\mu_{TA}.
$$

The two unit laws and associativity describe substitution or flattening of nested free structure. These equations are typed: the unit composites start at $TA$, while the associativity composites start at $T^3A$.
