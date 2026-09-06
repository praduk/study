## Limits and continuity

Know these local models:

$$
\frac{\sin x}{x}\to1,\quad
\frac{1-\cos x}{x^2}\to\frac12,\quad
\frac{e^x-1}{x}\to1,\quad
\frac{\ln(1+x)}x\to1
\qquad(x\to0).
$$

Also $(1+1/n)^n\to e$. Factor, rationalize, compare dominant terms, or use a Taylor expansion before invoking l'Hospital's rule. L'Hospital applies only to a verified $0/0$ or $\infty/\infty$ form under its hypotheses.

$f$ is continuous at $a$ exactly when $\lim_{x\to a}f(x)=f(a)$. A continuous function on $[a,b]$ is bounded, attains extrema, is uniformly continuous, and has the intermediate-value property.

## Derivative anchors

$$
(fg)'=f'g+fg',\qquad
\left(\frac fg\right)'=\frac{f'g-fg'}{g^2},\qquad
(f\circ g)'=(f'\circ g)g'.
$$

$$
\frac d{dx}e^x=e^x,\quad
\frac d{dx}a^x=a^x\ln a,\quad
\frac d{dx}\ln|x|=\frac1x.
$$

$$
(\sin x)'=\cos x,\quad (\cos x)'=-\sin x,\quad
(\tan x)'=\sec^2x.
$$

$$
(\arcsin x)'=\frac1{\sqrt{1-x^2}},\quad
(\arctan x)'=\frac1{1+x^2},\quad
(\operatorname{arcsec}x)'=\frac1{|x|\sqrt{x^2-1}}.
$$

If $y=f(x)$ and $f'(x)\ne0$, then

$$
(f^{-1})'(y)=\frac1{f'(x)}.
$$

Logarithmic differentiation is efficient for variable powers and long products. For $y=u(x)^{v(x)}$, write $\ln y=v\ln u$ on a domain where the expression is defined.

## Theorem triggers

- **Rolle:** continuous on $[a,b]$, differentiable on $(a,b)$, equal endpoint values $\Rightarrow f'(c)=0$.
- **Mean Value:** same regularity $\Rightarrow f'(c)=(f(b)-f(a))/(b-a)$.
- If $f'>0$, then $f$ is strictly increasing; if $f'=0$ throughout an interval, $f$ is constant.
- If $|f'|\le M$, then $|f(x)-f(y)|\le M|x-y|$.

Never use a theorem without checking its interval and differentiability hypotheses.

## Optimization and shape

Test endpoints and every interior critical point for absolute extrema on a closed interval. A critical point occurs where $f'=0$ or $f'$ fails to exist while $f$ remains defined.

At a critical point, $f''>0$ gives a local minimum and $f''<0$ a local maximum; $f''=0$ is inconclusive. An inflection point requires a change of concavity, not merely $f''=0$.

Linear approximation at $a$ is

$$
f(x)\approx f(a)+f'(a)(x-a).
$$

## Taylor deck

$$
e^x=1+x+\frac{x^2}{2!}+\cdots,
$$

$$
\sin x=x-\frac{x^3}{3!}+\frac{x^5}{5!}-\cdots,
\qquad
\cos x=1-\frac{x^2}{2!}+\frac{x^4}{4!}-\cdots,
$$

$$
\frac1{1-x}=\sum_{n=0}^\infty x^n\quad(|x|<1),
$$

$$
\ln(1+x)=x-\frac{x^2}{2}+\frac{x^3}{3}-\cdots\quad(-1<x\le1),
$$

$$
\arctan x=x-\frac{x^3}{3}+\frac{x^5}{5}-\cdots\quad(-1\le x\le1).
$$

At $x=\pm1$, the arctangent series converges conditionally; the preliminary sheet's exclusion of $\pm i$ belongs to complex singularity analysis, not the real interval statement.

Lagrange remainder:

$$
R_n(x)=\frac{f^{(n+1)}(c)}{(n+1)!}(x-a)^{n+1}
$$

for some $c$ between $a$ and $x$.

## Fast error checks

Check domain before differentiating, distinguish a corner from a cusp or vertical tangent, do not cancel a zero denominator, and remember that a local extremum need not be an absolute extremum.
