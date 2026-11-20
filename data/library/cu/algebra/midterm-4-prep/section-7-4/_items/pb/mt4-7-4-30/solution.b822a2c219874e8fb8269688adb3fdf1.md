Let $\pi:R\to R/I$ be the @[quotient projection]mt4-quotient-projection and let $N$ be the @[nilradical]mt4-nilradical of $R/I$. For each $r\in R$, the definition of a @[nilpotent element]mt4-nilpotent gives

$$
\begin{aligned}
\pi(r)\in N
&\iff \pi(r)^n=0\text{ for some }n\ge1\\
&\iff r^n\in I\text{ for some }n\ge1,
\end{aligned}
$$

because $\pi(r)^n=\pi(r^n)$ and $\ker\pi=I$. Thus the @[radical]mt4-ideal-radical is exactly $\pi^{-1}(N)$.

By @[Exercise 7.3.29]mt4-7-3-29, $N$ is an ideal of the commutative ring $R/I$. The @[ideal correspondence theorem]mt4-ideal-correspondence identifies its inverse image with an ideal of $R$ containing $I$. Hence $\sqrt I$ is an ideal and $I\subseteq\sqrt I$. Under the same correspondence, $(\sqrt I)/I=N$, as asserted.
