For states $i$ with energies $E_i$ and particle counts $N_i$, the heat-and-particle reservoir model assigns


$$
p_i=\Xi^{-1}e^{-\beta(E_i-\mu N_i)},\qquad \Xi=\sum_i e^{-\beta(E_i-\mu N_i)}.
$$


Require $0<\Xi<\infty$. $\mu$ has units J per particle, and fugacity $z=e^{\beta\mu}$ is dimensionless. Define the grand potential $\Omega=-k_BT\log\Xi$. Finite-volume fluctuations of $N$ are part of this ensemble, even if the experimental total system plus reservoir conserves particles.

For finite state sets, the natural coordinates are $(-\beta,\beta\mu)$, not $(T,\mu)$ themselves. The observables $(E,N)$ generate a covariance matrix by @physics:statistical:geometry:th:fisher-covariance. Energy-particle cross-fluctuations are its off-diagonal entries. Changing to laboratory coordinates requires the full parameter Jacobian in @physics:statistical:geometry:df:exponential-family; holding $T$ fixed isolates the usual particle-number susceptibility.
