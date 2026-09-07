If $a<c<b$ with $a,b$ in a connected subset of $\R$ and $c$ outside, its intersections with $(-\infty,c)$ and $(c,\infty)$ separate it. Thus connected subsets are intervals.

Conversely suppose an interval $J$ is separated into relatively open sets $U,V$, with $a\in U$, $b\in V$ and, after exchanging names if necessary, $a<b$. Let $c=\sup(U\cap[a,b])$. The interval contains $[a,b]$, so $c\in J$ and belongs to $U$ or $V$. If $c\in U$, then $c\ne b$ and relative openness gives a point of $U\cap[a,b]$ larger than $c$, contradiction. If $c\in V$, then $c\ne a$ and relative openness gives a left neighborhood of $c$ missing $U$, contradicting the supremum property. Hence intervals are connected, including the vacuous empty and singleton cases.

Finally a path joining opposite sides of a separation would have connected image, since its domain $[0,1]$ is connected. This contradiction proves path connectedness implies connectedness.
