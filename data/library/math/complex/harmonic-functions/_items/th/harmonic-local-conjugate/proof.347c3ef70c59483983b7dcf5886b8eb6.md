Fix $(x_0,y_0)$ in the rectangle and define

$$
v(x,y)=-\int_{x_0}^x u_y(t,y_0)\,dt+\int_{y_0}^y u_x(x,s)\,ds.
$$

Differentiating gives $v_y=u_x$, and, using $u_{xx}=-u_{yy}$,

$$
v_x=-u_y(x,y_0)+\int_{y_0}^y u_{xx}(x,s)\,ds
=-u_y(x,y_0)-u_y(x,y)+u_y(x,y_0)=-u_y(x,y).
$$

The derivatives are continuous. Thus Cauchy–Riemann holds, and $u+iv$ is holomorphic. This proves local existence; it does not assert that arbitrary domains admit a global conjugate.
