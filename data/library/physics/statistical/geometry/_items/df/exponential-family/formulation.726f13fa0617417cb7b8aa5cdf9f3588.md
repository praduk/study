Fix a finite set of $r\ge1$ microstates, positive weights $w_i$, and real observables $A_a(i)$ for $a=1,\ldots,m$. An exponential family is

$$
p_i(\eta)=w_i\exp\left(\sum_a\eta^aA_a(i)-\Psi(\eta)\right),
\qquad \Psi(\eta)=\log\sum_iw_i e^{\sum_a\eta^aA_a(i)}.
$$

The parameters are conjugate to the observables, with each product $\eta^aA_a$ dimensionless. Finite sums make every $p_i$ positive and smooth for finite real parameters. The score functions are $s_a(i)=\partial_{\eta^a}\log p_i$, and the Fisher information tensor is

$$
G_{ab}(\eta)=\sum_i p_i(\eta)s_a(i)s_b(i).
$$

It is a @[Riemannian metric]math:diffgeo:connections:df:riemannian-metric when @[positive definite]math:algebra:linear-foundations:df:bilinear-forms. The family is minimal when no nonzero linear combination $\sum_ac^aA_a(i)$ is constant over all states. @physics:statistical:geometry:th:fisher-covariance proves that minimality is exactly the positive-definiteness condition here.

Under a smooth change of parameters $\eta=\eta(\theta)$, the score transforms by the chain rule, so $G'_{bc}=G_{ad}(\partial_b\eta^a)(\partial_c\eta^d)$. This makes $G$ a covariant tensor, not a matrix whose numerical entries should remain fixed under reparametrization. In the canonical ensemble, $m=1$, $\eta=-\beta$ and $A=E$; in the grand ensemble one uses $(\eta^1,\eta^2)=(-\beta,\beta\mu)$ and $(A_1,A_2)=(E,N)$.
