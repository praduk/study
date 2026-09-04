Let

$$
A_0=A\setminus g[B],\qquad A_{n+1}=g[f[A_n]],\qquad
C=\bigcup_{n\in\omega}A_n.
$$

Define

$$
h(a)=
\begin{cases}
f(a),&a\in C,\\
g^{-1}(a),&a\notin C.
\end{cases}
$$

The second case is defined because $a\notin C$ implies $a\notin A_0$, hence $a\in g[B]$; injectivity of $g$ gives a unique inverse value.

Each branch is injective. Their images are disjoint: if $c\in C$, $a\notin C$, and $f(c)=g^{-1}(a)$, then $a=g(f(c))$. Choose $n$ with $c\in A_n$; then $a\in A_{n+1}\subseteq C$, a contradiction. Thus $h$ is injective.

For surjectivity, take $b\in B$. If $b\in f[C]$, then $b=h(c)$ for some $c\in C$. Otherwise $g(b)\notin C$: it cannot lie in $A_0$ because it is in $g[B]$, and if it lay in some $A_{n+1}=g[f[A_n]]$, injectivity of $g$ would give $b\in f[C]$. Hence $h(g(b))=g^{-1}(g(b))=b$. Therefore $h$ is bijective.
