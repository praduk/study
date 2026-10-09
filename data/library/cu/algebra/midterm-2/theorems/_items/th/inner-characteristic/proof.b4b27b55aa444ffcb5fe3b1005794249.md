The map $c:G\to\operatorname{Aut}(G)$, $c(g)=c_g$, is a homomorphism because $c_gc_h(x)=ghx(gh)^{-1}=c_{gh}(x)$. Its image is by definition $\operatorname{Inn}(G)$. Its kernel consists of those $g$ commuting with every $x$, namely $Z(G)$. The First Isomorphism Theorem gives $G/Z(G)\cong\operatorname{Inn}(G)$.

For $\alpha\in\operatorname{Aut}(G)$, direct evaluation at $x$ gives

$$
\alpha c_g\alpha^{-1}(x)=\alpha(g)x\alpha(g)^{-1}=c_{\alpha(g)}(x).
$$

Thus automorphisms conjugate inner automorphisms to inner automorphisms, proving $\operatorname{Inn}(G)$ normal in $\operatorname{Aut}(G)$.

If $H$ is characteristic in $G$, all inner automorphisms preserve it, so $H$ is normal. If $H$ is characteristic in $K$ and $K$ characteristic in $G$, every automorphism of $G$ restricts to an automorphism of $K$ and hence preserves $H$, proving transitivity. If instead $K\nsubg G$, every conjugation by $g\in G$ restricts to an automorphism of $K$; characteristicity of $H$ in $K$ makes this restriction preserve $H$, proving $H\nsubg G$.
