## Core facts

Write $z=x+iy=re^{i\theta}$. Then $|zw|=|z||w|$, arguments add modulo $2\pi$, and De Moivre's formula efficiently computes powers and roots. Every nonzero complex number has $n$ distinct $n$th roots equally spaced on a circle. Complex conjugation reverses the sign of the argument and satisfies $z\overline z=|z|^2$.

If $f=u+iv$ is complex differentiable on an open set with continuous first partial derivatives, the Cauchy--Riemann equations

$$
u_x=v_y,\qquad u_y=-v_x
$$

characterize holomorphicity there. Holomorphic functions are analytic. The complex logarithm is multivalued globally; a single-valued analytic branch requires a suitable domain avoiding a loop around the origin.

Cauchy's theorem makes the integral of a holomorphic function around a closed contour vanish on appropriate simply connected domains. Cauchy's integral formula and its derivative form are

$$
f(a)=\frac{1}{2\pi i}\oint_C\frac{f(z)}{z-a}\,dz,
\qquad
f^{(n)}(a)=\frac{n!}{2\pi i}\oint_C\frac{f(z)}{(z-a)^{n+1}}\,dz.
$$

Taylor series describe holomorphic behavior near regular points. Laurent series also allow negative powers and classify isolated singularities as removable, poles, or essential. The residue is the coefficient of $(z-a)^{-1}$. For a simple pole of $g/h$ with $h(a)=0$ and $h'(a)\ne0$, the residue is $g(a)/h'(a)$. The residue theorem multiplies the sum of enclosed residues by $2\pi i$ for positive orientation.

Know Liouville's theorem, the maximum modulus principle, and their standard consequence, the fundamental theorem of algebra.

## Recognition cues

- A denominator $(z-a)^{n+1}$ with analytic numerator signals Cauchy's derivative formula.
- A rational contour integral usually reduces to enclosed poles and residues.
- Questions about a global logarithm or argument are really questions about winding and domain topology.
- Rewrite powers and roots in polar form before expanding algebraically.

## Edge cases and traps

- Only singularities inside the contour contribute.
- Clockwise orientation changes the sign.
- Cauchy--Riemann equations at one point do not by themselves prove holomorphicity nearby.
- A branch point is not an isolated pole.
- The radius of a Taylor series is limited by the nearest complex singularity, not merely a real one.
