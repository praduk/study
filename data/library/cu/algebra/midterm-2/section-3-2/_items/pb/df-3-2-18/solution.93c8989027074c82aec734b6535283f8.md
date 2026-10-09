Let $\pi:G\to G/N$ be the natural projection and restrict it to $H$. The restriction is a homomorphism with kernel $H\cap N$. By the First Isomorphism Theorem,

$$
\pi(H)\cong H/(H\cap N),
$$

so $|\pi(H)|$ divides $|H|$. On the other hand $\pi(H)$ is a subgroup of $G/N$, so its order divides $|G/N|=[G:N]$. Coprimality forces $|\pi(H)|=1$. Thus $\pi(h)=N$ for every $h\in H$, which means $h\in N$. Therefore $H\le N$.

**Technique:** look at the image in the quotient. Its order is simultaneously constrained by the domain and the codomain. Normality is needed to make $G/N$ a group.

**Foundations:** @cu:algebra:midterm-2:theorems:th:cosets-lagrange, @cu:algebra:midterm-2:theorems:th:first-isomorphism, @cu:algebra:midterm-2:theorems:th:orbit-stabilizer.
