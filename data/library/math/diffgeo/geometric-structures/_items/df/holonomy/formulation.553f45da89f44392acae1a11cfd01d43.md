For the @math:diffgeo:geometric-structures:df:bundle-connection $\nabla=d+A$, parallel transport along a parametrized curve $\gamma$ solves

$$
\dot s(t)+A_{\gamma(t)}(\dot\gamma(t))s(t)=0.
$$

The endpoint map is an invertible @[linear map]math:algebra:linear-foundations:df:vector-space between the fibers, obtained by a linear ODE and frame changes. The holonomy around a loop based at $p$ is this map from $E_p$ to itself. Holonomies of piecewise smooth based loops form a group: concatenation composes transport and reversal gives its inverse. A frame change conjugates the based holonomy, so its trace and eigenvalues are frame independent.

For a complex line connection, parallel transport along a closed loop is $\exp(-\oint A)$ in a global frame. For matrix connections at different points the matrices need not commute; transport is defined by the ODE, often denoted a path-ordered exponential. Zero curvature is a local statement and need not give identity holonomy on noncontractible loops; see @physics:fields:spinors-gauge:pb:pure-gauge for an explicit example.
