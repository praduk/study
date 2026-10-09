Every element of $M$ normalizes $M$, so $M\le N_G(M)\le G$. Maximality allows only the two possibilities $N_G(M)=M$ or $N_G(M)=G$. The latter means $gMg^{-1}=M$ for every $g$, which is exactly normality. Thus a nonnormal maximal subgroup is self-normalizing.

Now suppose $G$ finite and $M$ nonnormal. Under the action of $G$ on subgroups by conjugation, the stabilizer of $M$ is $N_G(M)=M$. Orbit–stabilizer therefore says there are $[G:M]$ distinct conjugate subgroups. Each has $|M|-1$ nonidentity elements because conjugation is a bijection and preserves the identity. The size of a union is at most the sum of the sizes, even when those sets overlap. Consequently

$$
\left|\left(\bigcup_{g\in G}gMg^{-1}\right)\setminus\{1\}\right|\le(|M|-1)[G:M].
$$


**Technique:** maximality turns an intermediate subgroup into a dichotomy; orbit–stabilizer then counts the conjugates, and a union bound counts their elements.

**Foundations:** @cu:algebra:midterm-2:theorems:th:orbit-stabilizer, @cu:algebra:midterm-2:definitions:df:normalizer-centralizer.
