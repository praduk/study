## Completeness and sequences

The least-upper-bound property of $\mathbb R$ drives monotone convergence, nested intervals, Bolzano-Weierstrass, and convergence of Cauchy sequences.

$s=\sup A$ means $s$ is an upper bound and every smaller number fails to be one. Equivalently, for every $\varepsilon>0$ there is $a\in A$ with $s-\varepsilon<a\le s$.

A sequence converges iff it is Cauchy in $\mathbb R^n$. Every bounded sequence in $\mathbb R^n$ has a convergent subsequence, but the full sequence need not converge.

## Topology of Euclidean space

Open means every point contains a small open ball still inside the set. Closed means containing all sequential limits of points in the set. In $\mathbb R^n$,

$$
K\text{ compact}\iff K\text{ closed and bounded}.
$$

This Heine-Borel equivalence is not valid in every metric or topological space.

Continuous images of compact sets are compact; real-valued continuous functions on compact sets attain extrema. Continuous functions on compact metric spaces are uniformly continuous.

## Function limits and convergence

Pointwise convergence fixes $x$ before taking $n\to\infty$. Uniform convergence requires one $N$ that works for every $x$:

$$
\sup_{x\in E}|f_n(x)-f(x)|\to0.
$$

Uniform limits of continuous functions are continuous. On a finite interval, uniform convergence permits interchange of limit and integral. Differentiation requires stronger hypotheses: typically uniform convergence of derivatives plus convergence at one point.

Weierstrass M-test:

$$
|f_n(x)|\le M_n\ \forall x,\quad \sum M_n<\infty
\quad\Longrightarrow\quad
\sum f_n\text{ converges uniformly and absolutely}.
$$

## Differentiability and integrability checks

Differentiability implies continuity, not conversely. The derivative need not be continuous. A bounded function on $[a,b]$ is Riemann integrable when its discontinuity set has measure zero; at an elementary level, continuous and monotone functions are integrable.

## Common counterexamples

- $x^n$ on $[0,1]$ converges pointwise to a discontinuous limit, so convergence is not uniform.
- $(0,1)$ is bounded but not compact.
- A continuous bijection need not have continuous inverse unless extra hypotheses such as compact-to-Hausdorff apply.
