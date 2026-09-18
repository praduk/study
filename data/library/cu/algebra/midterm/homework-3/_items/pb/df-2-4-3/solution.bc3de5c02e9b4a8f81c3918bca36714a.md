Elements of $H\cup Z(G)$ commute pairwise: elements of $H$ commute by hypothesis, and elements of $Z(G)$ commute with everything. Their inverses also commute, so any two finite words in these generators commute. Hence the generated subgroup is abelian. Equivalently every word can be collected as $hz$ with $h\in H,z\in Z(G)$, and such products commute.
For a counterexample choose $G=S_3$ and $H=\{1\}$. Then $H$ is abelian but $C_G(H)=G$, so the generated subgroup is the nonabelian group $S_3$. A nontrivial example is $G=S_3\times C_2$, $H=\{1\}\times C_2$, again with $C_G(H)=G$.

**Technique:** extend pairwise commutation from generators to words. Centralizing $H$ does not mean the centralizer is itself abelian.
