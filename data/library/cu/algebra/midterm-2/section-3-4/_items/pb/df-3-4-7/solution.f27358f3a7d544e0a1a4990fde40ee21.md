Proof by induction.

## Base Case
Let $G=\set{1}$, $H=\set{1}$, $1=H=G$ is the composition series.

## Inductive Case
Let $|G|>1$.  If $H=G$, then use the composition series for $G$.
If $H\neq G$, then there exists a maximal normal subgroup $J\nsubg G$ containing $H$ such that $J$ has a composition series that passes through $H$.  Then the composition series for $G$ that passes through $H$ is
$$
\underbrace{1 \cdots \nsubg H \nsubg \cdots J}_{\text{Composition series for $J$ containing $H$}} \nsubg G.
$$
