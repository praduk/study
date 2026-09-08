The right Cauchy–Green tensor is $C=F^TF$ and the Green strain is $E=(C-\mathbf1)/2$. A reference line element $dX$ has current squared length $dX^TCdX$, so its change is $2dX^TEdX$. These dimensionless tensors measure deformation relative to the chosen reference configuration.

Under an additional rigid rotation $F\mapsto RF$, with $R^TR=\mathbf1$, $C$ and $E$ remain unchanged. In particular $E=0$ for a pure rotation. A displacement gradient by itself does not have this property.

Intrinsically, with reference metric $G$ and spatial metric $g$, the current material metric is the covariant tensor $C=\chi^*g$, and $E=(\chi^*g-G)/2$. In Cartesian reference and spatial frames this is exactly $F^TF$ and $(F^TF-I)/2$. A spatial isometry $R$ satisfies $R^*g=g$, so $(R\circ\chi)^*g=\chi^*g$; this proves frame invariance without choosing matrix coordinates. The metric prerequisite is @math:diffgeo:connections:df:riemannian-metric.
