Necessity is equality of mixed partial derivatives. For sufficiency choose $(x_0,y_0)$ and define $F(x,y)=\int_{x_0}^x M(s,y_0)\,ds+\int_{y_0}^y N(x,t)\,dt$. Then $F_y=N$ and

$$
F_x=M(x,y_0)+\int_{y_0}^yN_x(x,t)\,dt=M(x,y).
$$

The rectangle ensures both integral paths stay in the domain. The graph assertion follows by the chain rule. Equality of mixed partials on an arbitrary punctured domain would not by itself guarantee a global potential.
