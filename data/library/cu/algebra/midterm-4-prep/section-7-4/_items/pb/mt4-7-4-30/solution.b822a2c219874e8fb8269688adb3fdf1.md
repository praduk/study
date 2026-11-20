Let $\pi:R\to R/I$ be the @[quotient projection]mt4-quotient-projection and let $N$ be the @[nilradical]mt4-nilradical of $R/I$. For every $r\in R$,

$$
\pi(r)\in N\iff \pi(r)^n=0\text{ for some }n\ge1
\iff r^n\in I\text{ for some }n\ge1.
$$

Consequently the @[radical of the ideal]mt4-ideal-radical is $\pi^{-1}(N)$. By @[Exercise 7.3.29]mt4-7-3-29, $N$ is an ideal of the commutative quotient. Its inverse image is an ideal: differences map to differences in $N$, and $\pi(sr)=\pi(s)\pi(r)\in N$ whenever $\pi(r)\in N$. This inverse image contains $I=\ker\pi$. Finally $\pi$ is onto, so $\pi(\sqrt I)=N$. Its image consists exactly of the cosets $r+I$ with $r\in\sqrt I$, namely $(\sqrt I)/I$.
