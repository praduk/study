Let $X$ be a set. Choose values $x_p\in X$ for every atom $p$, values $x_{\true},x_{\false}\in X$, a function $n:X\to X$, and a function $b_{\circ}:X\times X\to X$ for each binary connective $\circ$. There is a unique function $F:\mathsf{Form}\to X$ such that

$$F(p)=x_p,\quad F(\true)=x_{\true},\quad F(\false)=x_{\false},$$

$$F(\neg A)=n(F(A)),\qquad F(A\circ B)=b_{\circ}(F(A),F(B)).$$
