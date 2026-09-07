Let $U\subseteq\R^n$ be open and $f:U\to\R^n$ be continuously differentiable. If $Df(a)$ is invertible at $a\in U$, then there are open neighborhoods $U_0$ of $a$ and $V_0$ of $f(a)$ such that $f:U_0\to V_0$ is a bijection with continuously differentiable inverse. For $y\in V_0$,

$$
D(f^{-1})(y)=\bigl(Df(f^{-1}(y))\bigr)^{-1}.
$$

This is a local theorem: an everywhere invertible Jacobian does not by itself imply global injectivity. The existence proof is not included in this card; see Lebl, [Basic Analysis II](https://www.jirka.org/ra/realanal2.pdf), the chapter on several-variable derivatives. The derivative formula follows by differentiating $f\circ f^{-1}=\id$ using the chain rule.
