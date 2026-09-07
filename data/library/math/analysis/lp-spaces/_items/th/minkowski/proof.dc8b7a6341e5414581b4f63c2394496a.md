For $p=1$, integrate the pointwise triangle inequality; for $p=\infty$, take essential bounds. If $1<p<\infty$, the convexity bound $|f+g|^p\le2^{p-1}(|f|^p+|g|^p)$ first proves $f+g\in L^p$. Hölder then gives

$$
\int|f+g|^p\le\int(|f|+|g|)|f+g|^{p-1}
\le(\norm f_p+\norm g_p)\norm{f+g}_p^{p-1}.
$$

Divide when $\norm{f+g}_p>0$; the zero case is immediate. The convexity bound follows from convexity of $t^p$ at the midpoint of $|f|$ and $|g|$.
