## Core facts

For equally likely finite outcomes, probability is favorable outcomes divided by total outcomes. In general,

$$
P(A\cup B)=P(A)+P(B)-P(A\cap B),\qquad
P(A\mid B)=\frac{P(A\cap B)}{P(B)}.
$$

Events are independent when $P(A\cap B)=P(A)P(B)$, equivalently $P(A\mid B)=P(A)$ when defined. Bayes' rule reverses conditioning by combining conditional probabilities with prior probabilities. Sampling without replacement usually creates dependence; a complement often simplifies “at least one” events.

A discrete random variable has a probability mass function; a continuous one has a density whose integral gives probability. A cumulative distribution function is always nondecreasing and right-continuous. Linearity of expectation does not require independence:

$$
E[aX+bY+c]=aE[X]+bE[Y]+c.
$$

Variance satisfies $\operatorname{Var}(aX+b)=a^2\operatorname{Var}(X)$. For two variables,

$$
\operatorname{Var}(X+Y)=\operatorname{Var}(X)+\operatorname{Var}(Y)+2\operatorname{Cov}(X,Y),
$$

so variances add when covariance is zero, in particular under independence. Know the Bernoulli, binomial, geometric, Poisson, uniform, exponential, and normal families, including their means and variances.

In statistics, distinguish a population parameter from a sample statistic. The sample mean is unbiased for the population mean under independent identically distributed sampling. Its variance is $\sigma^2/n$. The law of large numbers concerns convergence of averages; the central limit theorem gives an approximate normalized distribution. Confidence level is a repeated-procedure property, not the posterior probability that a fixed parameter lies in one realized interval. Correlation measures linear association and does not establish causation.

## Recognition cues

- “Given that” calls for conditional probability and a reduced sample space.
- For expectations of sums, use linearity before finding a full distribution.
- For variances, check covariance or independence before adding.
- A binomial count requires a fixed number of independent trials with common success probability.

## Edge cases and traps

- Mutually exclusive positive-probability events are not independent.
- A density value can exceed $1$; its integral over the domain must equal $1$.
- In general, $E[g(X)]\ne g(E[X])$.
- Pairwise independence need not imply mutual independence.
- A small $p$-value is not the probability that the null hypothesis is true.
