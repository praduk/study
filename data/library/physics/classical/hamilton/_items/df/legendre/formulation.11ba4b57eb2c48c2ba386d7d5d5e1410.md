Define $p_i=L_{\dot q^i}$. A Lagrangian is regular at a point if the velocity @[Hessian]math:uganalysis:metric-multivariable:df:hessian $(L_{\dot q^i\dot q^j})$ is invertible there. The @[inverse function theorem]math:uganalysis:metric-multivariable:th:inverse-function then locally solves $\dot q=v(q,p,t)$. Its Hamiltonian is

$$
H(q,p,t)=p_iv^i-L(q,v,t).
$$

Regularity is local, not a promise of a globally one-to-one Legendre map. For $L=\dot q^TM(q)\dot q/2-V(q)$ with $M$ @[positive definite]math:algebra:linear-foundations:df:bilinear-forms, $H=p^TM^{-1}p/2+V$. The momentum is a covector; angular momentum, for example, is conjugate to an angular coordinate.

Intrinsically this is a map $TQ\to T^*Q$ obtained by differentiating $L$ along each velocity fiber. For natural mechanics it is precisely the metric duality in @physics:classical:geometry:df:kinetic-metric. Thus canonical momentum is a covector for geometric reasons, and not merely because a coordinate formula happens to carry a lower index.
