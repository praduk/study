For a @math:algebra:linear-foundations:df:vector-space $V$ over $K$, the algebraic dual is $V^*=\operatorname{Hom}_K(V,K)$, the space of all linear functionals. Evaluation is the pairing $(\ell,v)\mapsto\ell(v)$. If $(e_1,\ldots,e_n)$ is a finite basis, the dual basis $(e^1,\ldots,e^n)$ is characterized by $e^i(e_j)=\delta^i_j$; explicitly, $e^i$ reads the $i$th coordinate.

The annihilator of a subspace $U\subseteq V$ is $U^\circ=\{\ell\in V^*: \ell(u)=0\text{ for every }u\in U\}$. The dual map of $T:V\to W$ is $T^*:W^*\to V^*$, $T^*\ell=\ell\circ T$. This use of a star denotes precomposition, not a Hilbert-space adjoint.

On a normed space, the @[continuous dual]math:analysis:banach-spaces:df:banach-operator contains only bounded linear functionals; see @math:analysis:banach-spaces:df:banach-operator. In infinite dimension it must not silently be identified with the algebraic dual. No metric is needed to define either evaluation or the algebraic dual map.
