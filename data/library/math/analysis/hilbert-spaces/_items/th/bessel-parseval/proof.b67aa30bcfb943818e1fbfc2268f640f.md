Let $p_N=\sum_{n=1}^N\iprod{x}{e_n}e_n$. Orthogonality gives
$\norm{x-p_N}^2=\norm x^2-\sum_{n=1}^N|\iprod{x}{e_n}|^2\ge0$,
proving Bessel. If the span is dense, choose a finite combination $v$ within $\epsilon$ of $x$. For $N$ containing all its indices, orthogonal projection minimizes distance, so $\norm{x-p_N}\le\norm{x-v}<\epsilon$. Thus $p_N\to x$, and the same identity yields Parseval.
