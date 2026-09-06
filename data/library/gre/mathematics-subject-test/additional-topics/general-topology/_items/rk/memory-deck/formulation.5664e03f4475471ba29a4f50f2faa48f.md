## Topology and bases

A topology contains $\varnothing$ and $X$, is closed under arbitrary unions, and is closed under finite intersections. A basis $\mathcal B$ covers $X$ and refines intersections: if $x\in B_1\cap B_2$, some $B_3\in\mathcal B$ satisfies $x\in B_3\subseteq B_1\cap B_2$.

Closure, interior, and boundary:

$$
\overline A=\bigcap\{F:F\text{ closed and }A\subseteq F\},
$$

$$
A^\circ=\bigcup\{U:U\text{ open and }U\subseteq A\},
\qquad
\partial A=\overline A\setminus A^\circ.
$$

$x\in\overline A$ iff every neighborhood of $x$ meets $A$.

## Continuity and constructions

$f:X\to Y$ is continuous iff preimages of open sets are open. A homeomorphism is a bijection whose map and inverse are continuous. Subspace topology uses intersections with the ambient open sets; product topology has basis $U\times V$; quotient topology declares $U$ open when its full preimage is open.

## Compactness and separation

Compact means every open cover has a finite subcover. Continuous images of compact spaces are compact. Closed subsets of compact spaces are compact. Compact subsets of Hausdorff spaces are closed.

$T_1$ means singletons are closed. Hausdorff means distinct points have disjoint neighborhoods. A continuous bijection from compact to Hausdorff is a homeomorphism.

## Connectedness

A connected space has no separation into two disjoint nonempty open sets. Continuous images of connected spaces are connected. Connected subsets of $\mathbb R$ are intervals. Path connected implies connected, but not conversely in general.

## Metric-space equivalences

In metric spaces, compactness, sequential compactness, and complete plus totally bounded are equivalent. Closed and bounded is equivalent to compact only in special settings such as finite-dimensional Euclidean space.

## Counterexample habit

Test broad claims against the discrete topology, indiscrete topology, cofinite topology, an open interval, and an infinite set with the discrete metric. These examples separate properties that coincide in $\mathbb R^n$ but not generally.
