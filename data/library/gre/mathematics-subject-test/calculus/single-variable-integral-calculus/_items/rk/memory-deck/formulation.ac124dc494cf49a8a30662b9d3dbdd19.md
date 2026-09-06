## Fundamental theorem and symmetry

If $f$ is continuous and $F(x)=\int_a^x f(t)\,dt$, then $F'(x)=f(x)$. If $F'=f$, then

$$
\int_a^b f(x)\,dx=F(b)-F(a).
$$

For symmetric bounds,

$$
\int_{-a}^a f(x)\,dx=0\quad\text{if $f$ is odd},
$$

$$
\int_{-a}^a f(x)\,dx=2\int_0^a f(x)\,dx\quad\text{if $f$ is even}.
$$

With variable bounds, differentiate each bound and preserve its sign:

$$
\frac d{dx}\int_{u(x)}^{v(x)}f(t)\,dt=f(v(x))v'(x)-f(u(x))u'(x).
$$

## Antiderivative anchors

$$
\int x^n\,dx=\frac{x^{n+1}}{n+1}+C\ (n\ne-1),
\quad \int\frac{dx}{x}=\ln|x|+C,
$$

$$
\int e^x\,dx=e^x+C,
\quad \int\frac{dx}{1+x^2}=\arctan x+C,
\quad \int\frac{dx}{\sqrt{1-x^2}}=\arcsin x+C.
$$

Pair derivative patterns: $\sec^2x\leftrightarrow\tan x$, $\sec x\tan x\leftrightarrow\sec x$, and analogous cosecant pairs with a minus sign.

## Technique selection

1. Simplify and look for symmetry.
2. Use substitution for an inner function and its derivative.
3. Use integration by parts for products such as polynomial times exponential/trigonometric/logarithmic:

$$
\int u\,dv=uv-\int v\,du.
$$

4. For rational functions, divide first if improper, then use partial fractions.
5. For powers of sine and cosine, save an odd factor or use power reduction when both powers are even.
6. For $\sqrt{a^2-x^2}$, $\sqrt{a^2+x^2}$, and $\sqrt{x^2-a^2}$, consider $x=a\sin\theta$, $a\tan\theta$, and $a\sec\theta$, respectively.

## Improper integrals

Replace every infinite endpoint or singularity by a separate limit. A sum of improper pieces converges only if every piece converges.

$$
\int_1^\infty x^{-p}\,dx\text{ converges iff }p>1,
$$

$$
\int_0^1 x^{-p}\,dx\text{ converges iff }p<1.
$$

An unbounded integrand can still be integrable. Comparison works only with the inequality in the useful direction and usually with nonnegative functions.

## Applications

$$
A=\int_a^b(\text{top}-\text{bottom})\,dx,
$$

$$
V_{\text{washers}}=\pi\int_a^b(R^2-r^2)\,dx,
\qquad
V_{\text{shells}}=2\pi\int_a^b(\text{radius})(\text{height})\,dx.
$$

$$
L=\int_a^b\sqrt{1+(f'(x))^2}\,dx,
$$

$$
S=2\pi\int_a^b f(x)\sqrt{1+(f'(x))^2}\,dx
$$

for rotation about the $x$-axis when $f\ge0$.

Average value:

$$
f_{\rm avg}=\frac1{b-a}\int_a^b f(x)\,dx.
$$

## Fast checks

Definite integrals do not carry $+C$. A geometric area is nonnegative, but a definite integral is signed. Confirm bounds after substitution, and include the Jacobian or radius factor required by the coordinate system.
