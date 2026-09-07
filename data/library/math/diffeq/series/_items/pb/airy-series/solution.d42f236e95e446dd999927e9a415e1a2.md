Writing $y=\sum_{n\ge0}a_nx^n$, the constant coefficient gives $a_2=0$ and for $n\ge1$,

$$
a_{n+2}=-\frac{a_{n-1}}{(n+2)(n+1)}.
$$

With $a_0=1$, $a_1=a_2=0$, only multiples of $3$ survive. Thus $y=1-x^3/6+x^6/180-x^9/12960+\cdots$. The ratio of consecutive nonzero terms in absolute value is $|x|^3/[(3k+3)(3k+2)]$, tending to zero for every fixed $x$. The series has infinite radius and may be differentiated termwise on compact intervals. The recurrence therefore verifies the equation and initial values; uniqueness of the linear initial-value problem proves it is the desired solution.
