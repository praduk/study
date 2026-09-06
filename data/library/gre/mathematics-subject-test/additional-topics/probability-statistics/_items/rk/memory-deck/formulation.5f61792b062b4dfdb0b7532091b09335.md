## Probability rules

$$
P(A^c)=1-P(A),\qquad
P(A\cup B)=P(A)+P(B)-P(A\cap B),
$$

$$
P(A\mid B)=\frac{P(A\cap B)}{P(B)}.
$$

Independence means $P(A\cap B)=P(A)P(B)$; it is not the same as disjointness. Bayes:

$$
P(A_i\mid B)=\frac{P(B\mid A_i)P(A_i)}{\sum_jP(B\mid A_j)P(A_j)}.
$$

## Random variables

$$
E[X]=\sum_x xP(X=x),\qquad
\operatorname{Var}(X)=E[X^2]-E[X]^2.
$$

Expectation is always linear. In general,

$$
\operatorname{Var}(aX+bY)=a^2\operatorname{Var}X+b^2\operatorname{Var}Y+2ab\operatorname{Cov}(X,Y).
$$

For independent variables the covariance term is zero; zero covariance alone does not generally imply independence.

For a continuous density $f$, $f\ge0$, $\int f=1$, and $P(a\le X\le b)=\int_a^bf(x)\,dx$. The cumulative distribution function is $F(x)=P(X\le x)$.

## Common distributions

$$
X\sim\operatorname{Bin}(n,p):\quad E[X]=np,\quad \operatorname{Var}X=np(1-p),
$$

$$
X\sim\operatorname{Geom}(p)\text{ on }1,2,\dots:\quad E[X]=1/p,
$$

$$
X\sim\operatorname{Poisson}(\lambda):\quad E[X]=\operatorname{Var}X=\lambda.
$$

For $X\sim N(\mu,\sigma^2)$, standardize with $Z=(X-\mu)/\sigma$.

## Descriptive statistics

The mean is sensitive to outliers; the median is resistant. Sample variance commonly uses denominator $n-1$, while population variance uses $n$. Correlation is covariance divided by the product of standard deviations and lies in $[-1,1]$ when defined; correlation does not establish causation.

## Counting first

For finite equally likely outcomes, compute favorable over total only after defining the sample space consistently. Conditional probability changes the denominator; many short GRE errors come from keeping the original denominator.
