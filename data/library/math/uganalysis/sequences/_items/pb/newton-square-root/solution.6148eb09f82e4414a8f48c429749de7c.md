All terms are positive. Squaring the recursion gives

$$
x_{n+1}^2-a=\frac14(x_n-a/x_n)^2\ge0.
$$

Thus $x_n^2\ge a$ for $n\ge2$, and $x_{n+1}-x_n=(a-x_n^2)/(2x_n)\le0$ for those indices. The tail is decreasing and nonnegative, so it has a limit $L\ge0$. In fact $x_n\le x_2$ and $x_n^2\ge a$ imply $x_n\ge a/x_n\ge a/x_2>0$, hence $L>0$. Passing to the recursion gives $L=(L+a/L)/2$, so $L^2=a$. The positive solution of this equation is unique because positive squaring is strictly increasing; it is $\sqrt a$. This argument also proves existence of the positive square root without presupposing it.
