Forward Euler for $y'=f(t,y)$ uses $y_{n+1}=y_n+h f(t_n,y_n)$. Under suitable smoothness and Lipschitz assumptions, the one-step solution error is $O(h^2)$ and the accumulated error on a fixed time interval is $O(h)$. For $y'=\lambda y$, each step multiplies by $1+h\lambda$; decay requires $|1+h\lambda|<1$. A tolerance is not the same as a proved global error bound.

**Pattern practice.** @gre:mathematics-subject-test:additional-topics:numerical-analysis:pb:euler-update; @gre:mathematics-subject-test:additional-topics:numerical-analysis:pb:euler-stability.
