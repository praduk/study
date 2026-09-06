**Correct choice: (B).**

**Fastest valid route.** For $f(x)=x^2-2$, Newton's update simplifies to

$$
x_{k+1}=\frac12\left(x_k+\frac{2}{x_k}\right).
$$

Hence

$$
x_1=\frac12(1+2)=\frac32,
\qquad
x_2=\frac12\left(\frac32+\frac{4}{3}\right)=\frac{17}{12}.
$$

**Verification.** Applying the unsimplified formula at $x_1=3/2$ gives

$$
x_2=\frac32-\frac{(3/2)^2-2}{2(3/2)}
=\frac32-\frac{1/4}{3}
=\frac32-\frac1{12}
=\frac{17}{12}.
$$
