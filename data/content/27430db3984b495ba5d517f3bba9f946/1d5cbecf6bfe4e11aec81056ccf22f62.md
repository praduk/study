For (1), for arbitrary $x$,

$$
\begin{aligned}
x\in A\setminus(B\cup C)
&\leftrightarrow x\in A\land x\notin B\land x\notin C\\
&\leftrightarrow x\in(A\setminus B)\cap(A\setminus C).
\end{aligned}
$$

Extensionality gives the equality.

For (2),

$$
\begin{aligned}
x\in A\cap\bigcup\mathcal F
&\leftrightarrow x\in A\land\exists X\in\mathcal F\,(x\in X)\\
&\leftrightarrow\exists X\in\mathcal F\,(x\in A\cap X)\\
&\leftrightarrow x\in\bigcup\{A\cap X:X\in\mathcal F\}.
\end{aligned}
$$

Again apply Extensionality.

For (3), if $A\subseteq B$ and $X\subseteq A$, then $X\subseteq B$; hence every member of $\mathcal{P}(A)$ belongs to $\mathcal{P}(B)$. Conversely, if
$\mathcal{P}(A)\subseteq\mathcal{P}(B)$, then $A\in\mathcal{P}(A)$, so
$A\in\mathcal{P}(B)$ and therefore $A\subseteq B$.
