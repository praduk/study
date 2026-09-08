For $T\in\mathcal B(H)$ on a @[Hilbert space]math:analysis:hilbert-spaces:df:hilbert, its adjoint is the unique bounded operator $T^*$ satisfying

$$
\iprod{Tx}{y}=\iprod{x}{T^*y}\quad(x,y\in H).
$$

Existence follows by applying Riesz representation to the functional $x\mapsto\iprod{Tx}{y}$ for each fixed $y$; uniqueness gives linearity in $y$, and $\norm{T^*y}\le\norm T\norm y$ gives boundedness. A bounded operator is self-adjoint when $T=T^*$. The domain qualifier matters for unbounded operators, which are outside this definition.
