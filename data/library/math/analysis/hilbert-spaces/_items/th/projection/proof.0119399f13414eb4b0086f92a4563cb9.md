Let $d=\inf_{v\in M}\norm{x-v}$ and choose $m_n\in M$ with $\norm{x-m_n}\to d$. The @[parallelogram identity]math:analysis:hilbert-spaces:th:cauchy-schwarz gives

$$
\norm{m_n-m_k}^2
=2\norm{x-m_n}^2+2\norm{x-m_k}^2
-4\norm{x-(m_n+m_k)/2}^2
\le2\norm{x-m_n}^2+2\norm{x-m_k}^2-4d^2.
$$

Thus $(m_n)$ is Cauchy and converges to $m\in M$. It attains the distance. For $v\in M$, minimality of $\norm{x-m-tv}^2$ at real $t=0$ gives $\operatorname{Re}\iprod{x-m}{v}=0$; in the complex case apply this to $iv$ as well. Hence $x-m\perp M$. If two decompositions exist, their difference lies in both $M$ and $M^\perp$, so is zero. Finally Pythagoras gives $\norm{x-v}^2=\norm{x-m}^2+\norm{m-v}^2$, proving unique minimality.
