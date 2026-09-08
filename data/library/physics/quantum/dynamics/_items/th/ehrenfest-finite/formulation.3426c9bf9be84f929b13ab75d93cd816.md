Let $H(t)$ be a continuous Hermitian matrix, let $\psi$ solve $i\hbar\dot\psi=H\psi$, and let $A(t)$ be a differentiable matrix. Then


$$
\frac d{dt}\langle\psi|A\psi\rangle=\frac i\hbar\langle\psi|[H,A]\psi\rangle+\langle\psi|\dot A\psi\rangle.
$$


If $A$ is constant and commutes with $H(t)$ for all $t$, its expectation is conserved.

For Hermitian observables, @physics:quantum:geometry:th:projective-dynamics turns the expectation commutator into a Poisson bracket on ray space: $\dot h_A=\partial_t h_A+\{h_A,h_H\}$. Since $[A,H]=-[H,A]$, its displayed bracket convention reproduces exactly $i\langle[H,A]\rangle/\hbar$. This geometry explains the correspondence with Hamiltonian observable evolution while preserving the finite-dimensional domain assumptions.
