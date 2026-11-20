**Strategy.** Pass to $R/I$, where membership in $I$ becomes equality to zero. Show that $r\in\operatorname{rad} I$ exactly when its coset is nilpotent. The ideal correspondence will then give both conclusions.

**Recognize the preimage.** Let $\pi:R\to R/I$ be the @[quotient projection]mt4-quotient-projection and let $N=\mathfrak N(R/I)$ be the @[nilradical]mt4-nilradical of $R/I$. For any $r\in R$, the definition of a @[nilpotent element]mt4-nilpotent gives

$$
\begin{aligned}
\pi(r)\in N
&\iff \pi(r)^n=0 \text{ for some }n\ge 1\\
&\iff r^n\in I \text{ for some }n\ge 1.
\end{aligned}
$$

The second equivalence uses $\pi(r)^n=\pi(r^n)$ and $\ker\pi=I$. The last condition defines the @[radical]mt4-ideal-radical, so $\operatorname{rad} I=\pi^{-1}(N)$.

**Apply the correspondence.** By @[Exercise 7.3.29]mt4-7-3-29, $N$ is an ideal of the commutative ring $R/I$. The @[ideal correspondence theorem]mt4-ideal-correspondence sends $N$ to an ideal $\pi^{-1}(N)$ of $R$ containing $I$. Thus $\operatorname{rad} I$ is an ideal and $I\subseteq\operatorname{rad} I$. In the other direction, the correspondence sends $\operatorname{rad} I$ to $(\operatorname{rad} I)/I$, which therefore equals $N$.
