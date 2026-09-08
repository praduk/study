The formulas for $g_{\rm FS}$ and $\omega$ descend because unitary phase changes preserve the inner product of horizontal representatives. Nondegeneracy follows from $\omega(\xi,i\xi)=2\hbar\|\xi\|^2$. On a local unit section, the Berry form in @physics:quantum:geometry:df:berry-connection satisfies

$$
d\mathcal A(\xi,\eta)
=i\bigl(\langle\xi,\eta\rangle-\langle\eta,\xi\rangle\bigr)
=-2\operatorname{Im}\langle\xi,\eta\rangle
$$

for horizontal lifts. Thus $\omega=-\hbar\,d\mathcal A$ locally, and $d\omega=0$ by @math:diffgeo:forms:th:d-squared. These local identities prove closedness globally.

For horizontal $\xi$, differentiation gives $dh_H(\xi)=2\operatorname{Re}\langle(H-h_HI)\psi,\xi\rangle$. The proposed $X$ is horizontal, and conjugate linearity in the first slot gives $\omega(X,\xi)=dh_H(\xi)$. Nondegeneracy makes it the unique Hamiltonian field in the convention of @math:diffgeo:geometric-structures:df:symplectic. The omitted component $-ih_H\psi/\hbar$ changes only the unit representative's phase, so Schrödinger evolution has the same ray projection.

Finally $\{h_A,h_B\}=dh_A(X_{h_B})=2\operatorname{Im}\langle A\psi,B\psi\rangle/\hbar$. For Hermitian $A,B$, the expected commutator is $\langle A\psi,B\psi\rangle-\langle B\psi,A\psi\rangle$, proving the formula.
