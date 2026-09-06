## Differential calculus in several variables

$$
\nabla f=(f_x,f_y,f_z),\qquad D_{\mathbf u}f=\nabla f\cdot\mathbf u
$$

for a **unit** direction $\mathbf u$. The maximum directional derivative is $\|\nabla f\|$, attained in the gradient direction.

Chain rule along a path $\mathbf r(t)$:

$$
\frac d{dt}f(\mathbf r(t))=\nabla f(\mathbf r(t))\cdot\mathbf r'(t).
$$

Tangent plane to $z=f(x,y)$ at $(a,b)$:

$$
z=f(a,b)+f_x(a,b)(x-a)+f_y(a,b)(y-b).
$$

For a level surface $F(x,y,z)=k$, the gradient is normal:

$$
\nabla F(a,b,c)\cdot\langle x-a,y-b,z-c\rangle=0.
$$

At a critical point of $f(x,y)$, let $D=f_{xx}f_{yy}-f_{xy}^2$. Then $D>0$ with $f_{xx}>0$ gives a minimum, $D>0$ with $f_{xx}<0$ a maximum, $D<0$ a saddle, and $D=0$ no conclusion.

For a constraint $g=k$, solve $\nabla f=\lambda\nabla g$ plus the constraint, while separately checking points where $\nabla g=0$ and any boundary cases.

## Multiple integrals and coordinates

Reverse integration order by drawing the region, not by merely swapping symbols. For a change of variables,

$$
dA=\left|\frac{\partial(x,y)}{\partial(u,v)}\right|du\,dv.
$$

Coordinate Jacobians:

$$
dA=r\,dr\,d\theta,
$$

$$
dV=r\,dr\,d\theta\,dz\quad\text{(cylindrical)},
$$

$$
dV=\rho^2\sin\phi\,d\rho\,d\phi\,d\theta\quad\text{(spherical)}.
$$

The missing Jacobian factor is among the most common fast-test errors.

## Vector fields and line integrals

For $\mathbf F=\langle P,Q,R\rangle$,

$$
\nabla\cdot\mathbf F=P_x+Q_y+R_z,
$$

$$
\nabla\times\mathbf F=
\begin{vmatrix}
\mathbf i&\mathbf j&\mathbf k\\
\partial_x&\partial_y&\partial_z\\
P&Q&R
\end{vmatrix}.
$$

$$
\int_C f\,ds=\int_a^b f(\mathbf r(t))\|\mathbf r'(t)\|\,dt,
$$

$$
\int_C\mathbf F\cdot d\mathbf r=
\int_a^b\mathbf F(\mathbf r(t))\cdot\mathbf r'(t)\,dt.
$$

If $\mathbf F=\nabla\phi$, then the vector line integral is $\phi(B)-\phi(A)$. In the plane, $P_y=Q_x$ is sufficient on a simply connected domain when $P,Q$ have continuous first partial derivatives; holes and singularities matter.

## Three integral theorems

$$
\oint_{\partial D}P\,dx+Q\,dy=\iint_D(Q_x-P_y)\,dA
$$

for positive counterclockwise orientation.

$$
\oint_{\partial S}\mathbf F\cdot d\mathbf r=\iint_S(\nabla\times\mathbf F)\cdot\mathbf n\,dS
$$

with the boundary orientation induced by $\mathbf n$.

$$
\iint_{\partial E}\mathbf F\cdot\mathbf n\,dS=\iiint_E\nabla\cdot\mathbf F\,dV
$$

with outward orientation.

## Selection rule

Closed plane curve and $P\,dx+Q\,dy$: consider Green. Boundary of a surface and curl: Stokes. Closed surface and flux: divergence. Before computing, state the orientation.
