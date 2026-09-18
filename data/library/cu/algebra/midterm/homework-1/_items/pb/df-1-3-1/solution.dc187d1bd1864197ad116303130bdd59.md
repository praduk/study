Following each unused symbol until it returns gives

$$
\begin{aligned}
\sigma&=(1\ 3\ 5)(2\ 4),&\tau&=(1\ 5)(2\ 3),\\
\sigma^2&=(1\ 5\ 3),&\sigma\tau&=(2\ 5\ 3\ 4),\\
\tau\sigma&=(1\ 2\ 4\ 3),&\tau^2\sigma&=(1\ 3\ 5)(2\ 4).
\end{aligned}
$$

For instance, under $\sigma\tau$ the orbit is $2\mapsto5\mapsto3\mapsto4\mapsto2$, while $1$ is fixed. Since $\tau^2=1$, the last answer equals $\sigma$.

**Technique:** trace images right to left; use a visited-symbol checklist and omit fixed points only after checking them.
