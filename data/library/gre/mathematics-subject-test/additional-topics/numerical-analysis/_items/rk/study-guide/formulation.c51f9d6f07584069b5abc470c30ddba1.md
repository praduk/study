## Core facts

Absolute error is $|x-\widehat x|$ and relative error scales it by $|x|$ when $x\ne0$. Conditioning describes sensitivity of the mathematical problem to input perturbations; stability describes how an algorithm amplifies errors. A small residual need not imply a small forward error for an ill-conditioned problem. Floating-point subtraction of nearly equal numbers can cause catastrophic cancellation.

Bisection requires a sign change for a continuous function and halves the interval each step, giving reliable linear convergence. Newton's method uses

$$
x_{k+1}=x_k-\frac{f(x_k)}{f'(x_k)}
$$

and is typically quadratically convergent near a simple root, but it can fail with a poor starting value or a zero derivative. The secant method avoids derivatives and is usually superlinear but less predictable than bisection.

Gaussian elimination solves dense linear systems in $O(n^3)$ arithmetic operations. Pivoting improves numerical stability. LU factorization is valuable when several right-hand sides share a coefficient matrix. The condition number predicts worst-case relative sensitivity; normal equations can square the condition number in least-squares problems.

A degree-$n$ polynomial interpolant through $n+1$ distinct nodes is unique. High-degree interpolation at equally spaced nodes can oscillate; piecewise methods such as splines can be safer. Finite-difference derivatives balance truncation error against roundoff. The trapezoidal and Simpson rules approximate integrals; Simpson's rule is exact for polynomials through degree three when applied under its standard assumptions.

Forward Euler for $y'=f(t,y)$ uses $y_{k+1}=y_k+h f(t_k,y_k)$ and has first-order global accuracy. Smaller step size usually reduces truncation error but increases work and can expose roundoff or stiffness. Always distinguish local truncation error, global error, and a stopping tolerance.

## Recognition cues

- A guaranteed bracket and sign change suggest bisection.
- A smooth equation with a good initial guess suggests Newton's method.
- Repeated systems with one matrix suggest factoring once and reusing the factors.
- Nearly equal subtraction or a large condition number warns that displayed digits may be unreliable.

## Edge cases and traps

- Newton iterates are not guaranteed to stay in a bracket or converge.
- A zero residual in floating-point arithmetic does not certify an exact mathematical solution.
- Interpolation is not the same as least-squares approximation.
- Smaller step size is not unconditionally better once rounding and stability matter.
- Simpson's rule needs the correct node spacing and an even number of subintervals in its composite form.
