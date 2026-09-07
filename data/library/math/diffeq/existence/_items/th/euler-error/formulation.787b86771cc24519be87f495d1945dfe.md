Consider $y'=f(t,y)$ on $[0,T]$, with $f$ globally Lipschitz in $y$ with constant $L\ge0$ on this time strip. Suppose the exact solution has $\norm{y''(t)}\le K$. For $h=T/N$, let $Y_0=y(0)$ and $Y_{j+1}=Y_j+hf(jh,Y_j)$. If $L>0$,

$$
\norm{Y_j-y(jh)}\le\frac{Kh}{2L}(e^{Ljh}-1).
$$

For $L=0$, the bound is $Kjh^2/2$.
