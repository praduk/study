## Sequences

$a_n\to L$ means that for every $\varepsilon>0$, eventually $|a_n-L|<\varepsilon$. Every convergent sequence is bounded. A monotone bounded sequence converges. Distinct subsequential limits prove divergence.

For a recursively defined positive sequence, first prove boundedness and monotonicity before solving the candidate limit equation; the algebraic fixed points alone do not prove convergence.

## Series recognition

$$
\sum_{n=0}^\infty ar^n=\frac a{1-r}\quad(|r|<1),
\qquad
\sum\frac1{n^p}\text{ converges iff }p>1.
$$

If $\sum a_n$ converges, then $a_n\to0$; the converse is false.

- **Comparison/limit comparison:** best for positive terms resembling $1/n^p$.
- **Ratio:** factorials and exponentials.
- **Root:** an entire expression raised to the $n$th power.
- **Integral:** positive continuous decreasing model.
- **Alternating:** decreasing magnitudes tending to zero; the first omitted magnitude bounds the error.

Absolute convergence implies convergence. Conditional convergence means convergence without absolute convergence.

For $\sum c_n(x-a)^n$, find the radius first and test both endpoints separately. Differentiation and integration term by term preserve the radius, but endpoint behavior may change.

## First-order ODEs

Separable:

$$
y'=g(x)h(y)\quad\Longrightarrow\quad \frac{dy}{h(y)}=g(x)\,dx.
$$

Check equilibrium solutions lost by division by $h(y)$.

Linear:

$$
y'+p(x)y=q(x),\qquad \mu(x)=e^{\int p(x)\,dx},
$$

$$
(\mu y)'=\mu q,\qquad
y=\mu^{-1}\left(\int\mu q\,dx+C\right).
$$

Integrating factors belong to first-order linear equations; do not apply that cue indiscriminately to every linear ODE.

## Constant-coefficient equations

For $ay''+by'+cy=0$, solve $ar^2+br+c=0$.

$$
\begin{array}{c|c}
\text{roots}&\text{homogeneous solution}\\ \hline
r_1\ne r_2\in\mathbb R&C_1e^{r_1x}+C_2e^{r_2x}\\
r\text{ repeated}&(C_1+C_2x)e^{rx}\\
\alpha\pm i\beta&e^{\alpha x}(C_1\cos\beta x+C_2\sin\beta x)
\end{array}
$$

For $L[y]=g$, use $y=y_h+y_p$. In undetermined coefficients, multiply the trial by enough powers of $x$ to remove overlap with $y_h$.

## Systems and qualitative behavior

For $x'=Ax$, eigenpairs yield modes $e^{\lambda t}v$. Negative real parts give asymptotic decay; any positive real part gives instability. Opposite-sign real eigenvalues give a saddle. A real $2\times2$ system with nonzero purely imaginary conjugate eigenvalues is a center; zero or defective cases need separate analysis.

For scalar autonomous $x'=f(x)$, use the sign of $f$ on intervals between equilibria. Arrows toward an equilibrium mean stable; arrows away mean unstable.

## Traps

Do not infer series convergence from $a_n\to0$, do not skip power-series endpoints, do not discard equilibrium solutions during separation, and always use the initial conditions after obtaining the general solution.
