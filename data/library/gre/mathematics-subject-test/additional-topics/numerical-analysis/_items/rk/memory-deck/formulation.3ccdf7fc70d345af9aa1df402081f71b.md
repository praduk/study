## Error and conditioning

Absolute error is $|\widehat x-x|$; relative error is $|\widehat x-x|/|x|$ when $x\ne0$. Forward error measures the answer error; backward error asks how much the input must change to make the computed answer exact. A small residual need not imply small forward error for an ill-conditioned problem.

Cancellation from subtracting nearly equal numbers can destroy significant digits. Condition number measures sensitivity of the mathematical problem; stability measures sensitivity of the algorithm.

## Root finding

Bisection requires continuity and a sign change. After $n$ bisections the bracket length is

$$
\frac{b-a}{2^n}.
$$

Newton's method:

$$
x_{n+1}=x_n-\frac{f(x_n)}{f'(x_n)}.
$$

Near a simple root it is typically quadratically convergent, but it can diverge or encounter $f'=0$. Fixed-point iteration $x_{n+1}=g(x_n)$ is locally attractive when $|g'(r)|<1$.

## Interpolation and approximation

The unique polynomial of degree at most $n$ through $n+1$ distinct nodes can be written in Lagrange form:

$$
p(x)=\sum_{j=0}^ny_j\prod_{k\ne j}\frac{x-x_k}{x_j-x_k}.
$$

Interpolation passes through data; least squares minimizes residual size and generally does not interpolate every point.

Finite differences:

$$
f'(x)\approx\frac{f(x+h)-f(x)}h\quad\text{has truncation error }O(h),
$$

$$
f'(x)\approx\frac{f(x+h)-f(x-h)}{2h}\quad\text{has truncation error }O(h^2).
$$

## Quadrature

$$
T=\frac{b-a}{2}[f(a)+f(b)],
$$

$$
S=\frac{b-a}{6}\left[f(a)+4f\left(\frac{a+b}{2}\right)+f(b)\right].
$$

The one-panel trapezoid rule is exact for degree $1$; Simpson's is exact through degree $3$. Composite Simpson requires an even number of subintervals.

## Linear systems

Gaussian elimination with pivoting is the default direct method. Factoring one matrix and reusing the factorization is efficient for repeated right-hand sides. Never form an explicit inverse merely to solve $Ax=b$ unless the problem specifically asks for it.
