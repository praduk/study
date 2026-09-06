## Function facts to recall cold

- For a composition $f\circ g$, first impose the domain of $g$, then require $g(x)$ to lie in the domain of $f$.
- A one-to-one function has an inverse on its range. Horizontal-line testing is the graph version.
- $y=f(x-h)+k$ moves the graph right by $h$ and up by $k$; $y=af(bx)$ scales outputs by $a$ and inputs by $1/|b|$, with reflections when a factor is negative.
- Even means $f(-x)=f(x)$; odd means $f(-x)=-f(x)$.
- For real logarithms, the argument must be positive. For even roots, the radicand must be nonnegative. Denominator restrictions survive cancellation.

## Trigonometric anchor deck

Reciprocals and quotients:

$$
\tan x=\frac{\sin x}{\cos x},\quad
\cot x=\frac{\cos x}{\sin x},\quad
\sec x=\frac1{\cos x},\quad
\csc x=\frac1{\sin x}.
$$

Pythagorean families:

$$
\sin^2x+\cos^2x=1,\qquad 1+\tan^2x=\sec^2x,
\qquad 1+\cot^2x=\csc^2x.
$$

Parity, periodicity, and cofunctions:

$$
\sin(-x)=-\sin x,\quad \cos(-x)=\cos x,\quad \tan(-x)=-\tan x,
$$

$$
\sin(x+2\pi)=\sin x,\quad \cos(x+2\pi)=\cos x,\quad \tan(x+\pi)=\tan x,
$$

$$
\sin\left(\frac\pi2-x\right)=\cos x,
\quad
\cos\left(\frac\pi2-x\right)=\sin x.
$$

**Critical correction.** Supplementary angles do not swap sine and cosine:

$$
\sin(\pi-x)=\sin x,\qquad \cos(\pi-x)=-\cos x,\qquad \tan(\pi-x)=-\tan x.
$$

The swap belongs to $\pi/2-x$. Use the unit circle rather than a verbal mnemonic when signs matter.

For $0,\pi/6,\pi/4,\pi/3,\pi/2$, the sine numerators are
$0,1,\sqrt2,\sqrt3,2$ over $2$; cosine reverses them. Quadrant signs follow **all, sine, tangent, cosine**.

## Sum, difference, and derived families

Memorize only these two anchors:

$$
\sin(x+y)=\sin x\cos y+\cos x\sin y,
$$

$$
\cos(x+y)=\cos x\cos y-\sin x\sin y.
$$

Replace $y$ by $-y$ for differences. Setting $y=x$ gives

$$
\sin 2x=2\sin x\cos x,
$$

$$
\cos 2x=\cos^2x-\sin^2x=1-2\sin^2x=2\cos^2x-1.
$$

Thus

$$
\sin^2x=\frac{1-\cos2x}{2},\qquad
\cos^2x=\frac{1+\cos2x}{2}.
$$

Half-angle square roots require a quadrant sign:

$$
\sin\frac{x}{2}=\pm\sqrt{\frac{1-\cos x}{2}},\qquad
\cos\frac{x}{2}=\pm\sqrt{\frac{1+\cos x}{2}}.
$$

Product-to-sum:

$$
\begin{aligned}
\sin x\cos y&=\frac{\sin(x+y)+\sin(x-y)}2,\\
\cos x\sin y&=\frac{\sin(x+y)-\sin(x-y)}2,\\
\cos x\cos y&=\frac{\cos(x+y)+\cos(x-y)}2,\\
\sin x\sin y&=\frac{\cos(x-y)-\cos(x+y)}2.
\end{aligned}
$$

Sum-to-product:

$$
\begin{aligned}
\sin x+\sin y&=2\sin\frac{x+y}{2}\cos\frac{x-y}{2},\\
\sin x-\sin y&=2\cos\frac{x+y}{2}\sin\frac{x-y}{2},\\
\cos x+\cos y&=2\cos\frac{x+y}{2}\cos\frac{x-y}{2},\\
\cos x-\cos y&=-2\sin\frac{x+y}{2}\sin\frac{x-y}{2}.
\end{aligned}
$$

Memory check: all four have an outside $2$ and half-sum/half-difference arguments; the cosine difference is the only one with an initial minus sign.

## Coordinate geometry anchors

$$
m=\frac{y_2-y_1}{x_2-x_1},\qquad
d=\sqrt{(x_2-x_1)^2+(y_2-y_1)^2}.
$$

Distance from $(x_0,y_0)$ to $ax+by+c=0$ is

$$
\frac{|ax_0+by_0+c|}{\sqrt{a^2+b^2}}.
$$

Standard conics:

$$
(x-h)^2+(y-k)^2=r^2,
$$

$$
\frac{x^2}{a^2}+\frac{y^2}{b^2}=1,\quad c^2=a^2-b^2,
$$

$$
\frac{x^2}{a^2}-\frac{y^2}{b^2}=1,\quad c^2=a^2+b^2,
\quad y=\pm\frac ba x.
$$

Polar conversion and polar area:

$$
x=r\cos\theta,\quad y=r\sin\theta,\quad r^2=x^2+y^2,
\qquad A=\frac12\int_\alpha^\beta r(\theta)^2\,d\theta.
$$

For $x=x(t)$ and $y=y(t)$,

$$
\frac{dy}{dx}=\frac{dy/dt}{dx/dt},\qquad
\frac{d^2y}{dx^2}=\frac{d}{dt}(dy/dx)\bigg/\frac{dx}{dt}.
$$

## Retrieval drill

From memory, reconstruct the two angle-addition formulas. Derive double-angle, power-reduction, and product-to-sum from them. Then draw one unit circle and label exact values and signs. Derivation is more reliable than memorizing isolated sign patterns.
