For functors $F:\mathcal C\to\mathcal D$ and $G:\mathcal D\to\mathcal C$, an adjunction $F\dashv G$ is a family of bijections

$$
\Phi_{A,B}:\Hom_{\mathcal D}(FA,B)\cong\Hom_{\mathcal C}(A,GB)
$$

natural in $A$ and $B$. Here $F$ is the left adjoint and $G$ the right adjoint. Naturality means

$$
\Phi_{A',B'}(v\,h\,F(u))=G(v)\Phi_{A,B}(h)u
$$

for $u:A'\to A$, $h:FA\to B$, and $v:B\to B'$. The two corresponding arrows are called transposes. An adjunction is extra data, not merely a coincidence of Hom-set cardinalities.
