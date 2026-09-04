**(ZFC convention for the full package.)** For cardinals $\kappa$ and $\lambda$, define

$$
\begin{aligned}
\kappa+\lambda
&=|(\{0\}\times\kappa)\cup(\{1\}\times\lambda)|,\\
\kappa\cdot\lambda
&=|\kappa\times\lambda|,\\
\kappa^\lambda
&=|\operatorname{Fun}(\lambda,\kappa)|,
\end{aligned}
$$

where $\operatorname{Fun}(\lambda,\kappa)$ is the set of functions from $\lambda$ to $\kappa$. The tagged union in the first line keeps the summands disjoint.

For a set-indexed family of cardinals $\langle\kappa_i:i\in I\rangle$, define

$$
\sum_{i\in I}\kappa_i
=
\left|\{\langle i,\alpha\rangle:i\in I\text{ and }\alpha<\kappa_i\}\right|
$$

and

$$
\prod_{i\in I}\kappa_i
=
\left|\{f:\operatorname{dom}(f)=I\text{ and }f(i)<\kappa_i
\text{ for every }i\in I\}\right|.
$$

Binary cardinal addition and multiplication of well-orderable sets are already well-defined in ZF: the displayed tagged union and Cartesian product can be explicitly well-ordered. In contrast, even when $\kappa$ and $\lambda$ are initial ordinals, ZF alone need not prove that $\operatorname{Fun}(\lambda,\kappa)$ is well-orderable, and an indexed sum or product over an arbitrary set $I$ presents the same issue. The initial-ordinal values in the full definition above therefore use ZFC. These are cardinal operations: only bijection type matters. They must not be confused with ordinal operations, which retain order-type information and need not commute.
