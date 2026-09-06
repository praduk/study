## Complex arithmetic and polar form

For $z=x+iy$,

$$
\overline z=x-iy,\qquad |z|^2=z\overline z,\qquad
\frac1z=\frac{\overline z}{|z|^2}\quad(z\ne0).
$$

Euler's formula gives $z=re^{i\theta}$. Products multiply moduli and add arguments; powers obey de Moivre. The $n$th roots are

$$
r^{1/n}e^{i(\theta+2\pi k)/n},\qquad k=0,\dots,n-1.
$$

Arguments are multivalued modulo $2\pi$ unless a branch is specified.

## Holomorphic functions

For $f=u+iv$, the Cauchy-Riemann equations are

$$
u_x=v_y,\qquad u_y=-v_x.
$$

With continuous first partials in a neighborhood, these equations imply holomorphicity there. Real and imaginary parts of a holomorphic function are harmonic:

$$
u_{xx}+u_{yy}=0,\qquad v_{xx}+v_{yy}=0.
$$

## Cauchy theory

On a simply connected domain where $f$ is holomorphic, closed contour integrals vanish. For positively oriented $C$ enclosing $a$,

$$
f^{(n)}(a)=\frac{n!}{2\pi i}\int_C\frac{f(z)}{(z-a)^{n+1}}\,dz.
$$

The ML estimate is $|\int_C f\,dz|\le ML$ when $|f|\le M$ on a contour of length $L$.

## Laurent series and residues

The residue is the coefficient of $(z-z_0)^{-1}$. For positively oriented $C$,

$$
\int_C f(z)\,dz=2\pi i\sum\operatorname{Res}(f,z_k).
$$

For a simple pole of $g/h$ with $h(z_0)=0$ and $h'(z_0)\ne0$,

$$
\operatorname{Res}\left(\frac gh,z_0\right)=\frac{g(z_0)}{h'(z_0)}.
$$

Principal part absent means removable, finitely many negative powers means a pole, and infinitely many means essential.

## Global anchors

Liouville: a bounded entire function is constant. The fundamental theorem of algebra follows. Maximum modulus: a nonconstant holomorphic function cannot attain an interior maximum of $|f|$.

## Traps

Orientation changes the sign of contour integrals. Cauchy's theorem requires the curve and its interior to stay in the domain; a singularity inside prevents the naive zero conclusion.
