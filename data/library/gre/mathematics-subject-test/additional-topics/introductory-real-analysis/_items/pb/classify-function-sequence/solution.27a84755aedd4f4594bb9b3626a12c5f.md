**Correct choice: (B).**

**Fastest valid route.** For every fixed $0\le x<1$, $x^n\to0$, while $f_n(1)=1$ for every $n$. Thus the pointwise limit is

$$
f(x)=\begin{cases}0,&0\le x<1,\\1,&x=1.\end{cases}
$$

It is discontinuous, so it cannot be the uniform limit of the continuous functions $f_n$.

**Verification.** On $[0,1)$ the error is $x^n$, whose supremum is $1$ for every $n$ because values approach $1$ as $x\to1^-$. At $x=1$ the error is $0$. Hence

$$
\sup_{x\in[0,1]}|f_n(x)-f(x)|=1,
$$

which does not tend to $0$. The convergence is pointwise but not uniform.
