## Core facts

A sequence $(a_n)$ converges to $L$ when every tolerance $\varepsilon>0$ eventually contains all terms: there is $N$ such that $n\ge N$ implies $|a_n-L|<\varepsilon$. Convergent sequences are bounded and have unique limits. Every bounded sequence in $\mathbb{R}^d$ has a convergent subsequence. A monotone bounded real sequence converges, and its limit is the appropriate supremum or infimum.

For a series $\sum a_n$, first test whether $a_n\to0$; failure forces divergence, but success proves nothing by itself. Know comparison and limit comparison, ratio and root tests, the integral test, alternating-series convergence, and absolute versus conditional convergence. Absolute convergence implies convergence. A power series converges inside its radius and diverges outside; endpoints require separate tests.

Pointwise convergence allows the index needed for a given accuracy to depend on $x$. Uniform convergence requires one index to work for every $x$ in the domain, equivalently $\sup_x|f_n(x)-f(x)|\to0$ when the supremum is meaningful. A uniform limit of continuous functions is continuous. Uniform convergence permits termwise integration on a compact interval; termwise differentiation needs additional hypotheses and is not automatic.

For continuous real functions, use the intermediate and extreme value theorems. A continuous function on a compact set is bounded, attains its extrema, and is uniformly continuous. Differentiability implies continuity, not conversely. The mean value theorem controls monotonicity and gives many inequalities. Continuous functions on closed bounded intervals are Riemann integrable; changing finitely many values does not change the integral.

In $\mathbb{R}^d$, compactness is equivalent to closedness and boundedness. Closed subsets contain their limit points; open sets contain a ball about each point. Completeness concerns Cauchy sequences, while compactness also forces convergent subsequences. Connected subsets of $\mathbb{R}$ are intervals.

## Recognition cues

- Look for monotonicity plus a bound before trying to compute a sequence explicitly.
- For uniform convergence, maximize the error or use continuity of the proposed limit as a quick obstruction.
- On a compact domain, reach first for extrema, uniform continuity, and convergent subsequences.
- At a power-series endpoint, discard the radius-of-convergence calculation and test the resulting numerical series directly.

## Edge cases and traps

- A bounded sequence need not converge; it only has a convergent subsequence in finite-dimensional Euclidean space.
- Pointwise limits of continuous functions can be discontinuous.
- Closed does not imply compact in $\mathbb{R}^d$ without boundedness.
- A derivative need not be continuous, but it has the intermediate value property.
- The alternating-series error estimate requires decreasing magnitudes tending to zero.
