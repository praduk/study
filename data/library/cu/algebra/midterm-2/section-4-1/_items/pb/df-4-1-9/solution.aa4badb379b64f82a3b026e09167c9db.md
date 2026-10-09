**(a) A translate is another H-orbit.** For $a\in A$ and $g\in G$,

$$
g(H\cdot a)=\{(ghg^{-1})\cdot(g\cdot a):h\in H\}=H\cdot(g\cdot a),
$$

because normality says $gHg^{-1}=H$. Thus $g$ sends an entire $H$-orbit onto an $H$-orbit. This defines a $G$-action on the collection of orbits. Given $O_i,O_j$, choose $a_i\in O_i,a_j\in O_j$. Transitivity on $A$ gives $g(a_i)=a_j$, and the displayed equality then gives $gO_i=O_j$. Hence the action on the orbit collection is transitive. Since $g$ is a bijection of $A$, its restriction is a bijection $O_i\to O_j$, proving equal sizes. Distinct $H$-orbits are disjoint, so each is also a block for $G$.

**(b) Count within an orbit.** The stabilizer of $a$ in $H$ is $H_a=H\cap G_a$. Orbit–stabilizer for the restricted action of $H$ gives $|O_1|=[H:H\cap G_a]$.

**Count the orbit collection.** Its stabilizer at $O_1=H\cdot a$ consists exactly of $HG_a$. If $gO_1=O_1$, then $g(a)=h(a)$ for some $h\in H$, so $h^{-1}g\in G_a$ and $g\in HG_a$. Conversely if $g=hk$ with $k\in G_a$, then $g(a)=h(a)\in O_1$, and part (a) says $gO_1$ is the $H$-orbit containing this point, hence $O_1$. As $H$ is normal, $HG_a$ is a subgroup. Orbit–stabilizer for the transitive action on the $r$ orbits therefore yields $r=[G:HG_a]$.

**Technique:** apply orbit–stabilizer twice: once to points under $H$, once to $H$-orbits under $G$. Identify the latter stabilizer explicitly.

**Foundations:** @cu:algebra:midterm-2:theorems:th:orbit-stabilizer, @cu:algebra:midterm-2:definitions:df:action-stabilizer.
