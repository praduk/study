Encode a well-ordering of a subset $B\subseteq A$ by the pair $\langle B,R\rangle$, where $R\subseteq B\times B$ well-orders $B$. All such codes lie in a set built from $\mathcal{P}(A)$ and $\mathcal{P}(A\times A)$, so Separation gives the set $W$ of the codes. Each member of $W$ has a unique ordinal order type. Replacement therefore yields the set $T$ of all those order types.

Let

$$
\theta=\sup\{\alpha+1:\alpha\in T\}.
$$

This is an ordinal. There can be no injection $j:\theta\to A$: otherwise transport the membership well-order on $\theta$ to $j[\theta]\subseteq A$. That well-ordering would have type $\theta$, so $\theta\in T$. The definition of $\theta$ would then imply $\theta+1\subseteq\theta$, impossible because $\theta\in\theta+1$ but $\theta\notin\theta$.

Thus at least one ordinal, namely $\theta$, does not inject into $A$. By Separation, the nonempty set

$$
\{\beta\in\theta+1:\text{there is no injection }\beta\to A\}
$$

has a least member. Call it $h(A)$. Its leastness is exactly the asserted property.
