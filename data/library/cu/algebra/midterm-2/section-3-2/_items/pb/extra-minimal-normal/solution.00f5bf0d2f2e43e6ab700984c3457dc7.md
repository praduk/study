**Step 1: show the intersection is normal in G.** Put $L=N\cap H$. For $h\in H$, normality of $N$ gives $hNh^{-1}=N$, and $hHh^{-1}=H$ because $h$ belongs to $H$. Hence $hLh^{-1}=L$. Every $n\in N$ centralizes $L$, since $L\le N$ and $N$ is abelian; thus $nLn^{-1}=L$. Every $g\in G$ is $nh$ because $NH=G$, so

$$
gLg^{-1}=n(hLh^{-1})n^{-1}=nLn^{-1}=L.
$$

Therefore $L\nsubg G$.

**Step 2: apply minimality and properness.** The subgroup $L$ lies in $N$, so it is either $1$ or $N$. If $L=N$, then $N\le H$, which implies $G=NH=H$, contrary to $H<G$. Consequently $N\cap H=1$.

**Step 3: test an arbitrary overgroup.** Let $H<K\le G$. Choose $k\in K\setminus H$, and write $k=nh$ with $n\in N,h\in H$. Then $n=kh^{-1}\in K\cap N$. Also $n\ne1$, since $n=1$ would give $k=h\in H$. Thus $N\cap K\ne1$.

As in Step 1, $N\cap K$ is normalized by $H$: elements of $H$ normalize $K$ because $H\le K$, and normalize $N$ because $N\nsubg G$. It is centralized by $N$ because $N$ is abelian. Since $G=NH$, this proves $N\cap K\nsubg G$. Minimality therefore gives $N\cap K=N$, so $N\le K$. We already have $H\le K$, hence $G=NH\le K$. Thus $K=G$.

Every subgroup strictly larger than $H$ is therefore $G$, which is exactly maximality. No finite-order hypothesis is needed.

**Technique:** turn an intersection into a normal subgroup using the two factors $N,H$; minimality gives a dichotomy. Then repeat that argument for each possible overgroup.

**Foundations:** @cu:algebra:midterm-2:theorems:th:cosets-lagrange, @cu:algebra:midterm-2:theorems:th:first-isomorphism, @cu:algebra:midterm-2:theorems:th:orbit-stabilizer.
