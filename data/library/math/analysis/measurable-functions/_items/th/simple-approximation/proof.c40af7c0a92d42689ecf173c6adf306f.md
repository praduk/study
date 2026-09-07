For finite $f(x)$ define

$$
s_n(x)=2^{-n}\left\lfloor2^n\min(f(x),n)\right\rfloor,
$$

and set $s_n(x)=n$ when $f(x)=\infty$. Each function has finitely many values and measurable level sets. The dyadic mesh is refined at each step and the truncation level increases, so $s_{n+1}\ge s_n$. If $f(x)<\infty$, eventually truncation is inactive and $0\le f(x)-s_n(x)<2^{-n}$. If $f(x)=\infty$, then $s_n(x)=n\to\infty$.
