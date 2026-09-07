A continuous-time Markov model has rates $w_{ij}\ge0$ for jumps from state $j$ to distinct state $i$ and probabilities obeying


$$
\dot p_i=\sum_{j\ne i}(w_{ij}p_j-w_{ji}p_i).
$$


A strictly positive probability vector $\pi$, with $\sum_i\pi_i=1$, obeys detailed balance if $w_{ij}\pi_j=w_{ji}\pi_i$ for every pair. It is then stationary by pairwise cancellation. Such rates can model weakly observed thermal transitions with $\pi$ chosen canonical, but this stochastic equation is a modeling assumption, not the exact isolated Hamiltonian dynamics.
