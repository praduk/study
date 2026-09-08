For a smooth real or complex @math:diffgeo:bundles-flows:df:vector-bundle $E\to M$, a connection is a @[linear map]math:algebra:linear-foundations:df:vector-space $\nabla:\Gamma(E)\to\Omega^1(M;E)$ with $\nabla(fs)=df\otimes s+f\nabla s$. Complex bundles use complex-linear fiber maps. Unlike a derivative of coordinate functions alone, it compares nearby fibers.

In a local frame, write $\nabla=d+A$, where $A$ is a matrix of one-forms. If section components change by $s'=g^{-1}s$ for a smooth invertible matrix $g$, then

$$
A'=g^{-1}Ag+g^{-1}dg,\qquad F_A=dA+A\w A.
$$

Matrix multiplication accompanies the @[wedge product]math:diffgeo:forms:df:exterior-algebra. Curvature acts by $\nabla^2s=F_As$. Direct substitution gives $F_{A'}=g^{-1}F_Ag$: expand $d(g^{-1})=-g^{-1}(dg)g^{-1}$ in the formula and cancel the terms containing two copies of $dg$ and the mixed $A,dg$ terms. Hence curvature is a globally defined endomorphism-valued two-form although $A$ depends on the frame. For the tangent bundle this recovers @math:diffgeo:connections:df:connection and @math:diffgeo:curvature:df:curvature.

The section notation and coefficient-valued exterior calculus are defined in @math:diffgeo:geometric-structures:df:bundle-valued-forms.
