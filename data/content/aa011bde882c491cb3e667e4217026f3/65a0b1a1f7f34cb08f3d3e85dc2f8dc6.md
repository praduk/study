Call $s$ an **approximation through $w$** if its domain is
$W_{\le w}=\{u\in W:u\le w\}$ and

$$
s(u)=\{s(v):v<u\}
\quad\text{for every }u\le w.
$$

Any two approximations agree on their common domain. Otherwise the well-order would supply a least point $u$ where they differ; they agree below $u$, so the displayed equation gives the same value at $u$, a contradiction.

We now prove by well-order induction that an approximation exists through every $w$. Assume the unique approximation $s_v$ exists for each $v<w$. Replacement collects the $s_v$ for $v<w$, and compatibility makes
$h=\bigcup_{v<w}s_v$ a function with domain $W_{<w}$. Set

$$
s_w=h\cup\{\langle w,\operatorname{ran}(h)\rangle\}.
$$

Then $s_w$ is an approximation through $w$. This includes the least-element case, when $h$ is empty. Replacement collects the unique $s_w$ for all $w\in W$, and their union is a function $f$ on $W$ satisfying
$f(w)=\{f(v):v<w\}$.

Well-order induction now proves simultaneously that every $f(w)$ is an ordinal, that $f$ is injective on $W_{\le w}$, and that

$$
u<v\quad\Longleftrightarrow\quad f(u)\in f(v)
\qquad(u,v\le w).
$$

At stage $w$, the earlier values already have these properties. If
$x\in f(v)\in f(w)$, with $v<w$, then the inductive hypothesis gives
$x=f(u)$ for some $u<v$, so $x\in f(w)$; hence $f(w)$ is transitive. By the inductive hypothesis, the restriction of $f$ to $W_{<w}$ is a bijection onto $f(w)$ that transfers $<$ to membership. Thus membership well-orders $f(w)$, so $f(w)$ is an ordinal. For every $u<w$, the defining equation gives $f(u)\in f(w)$, and therefore $f(u)\ne f(w)$ because membership on an ordinal is irreflexive. This extends injectivity through $w$. Finally, if $f(u)\in f(w)$, then $f(u)=f(t)$ for some $t<w$; the just-proved injectivity gives $u=t<w$. This proves the converse at the new stage, while pairs below $w$ are covered by the inductive hypothesis.

Replacement makes $\alpha=f[W]$ a set. The same equivalence shows that $\alpha$ is transitive and well-ordered by membership, hence is an ordinal, and that $f:W\to\alpha$ is an order isomorphism.

For uniqueness, suppose $g:W\to\beta$ is an isomorphism to an ordinal $\beta$. Well-order induction gives $g(w)=f(w)$: if they agree below $w$, then

$$
g(w)=\{g(v):v<w\}=\{f(v):v<w\}=f(w),
$$

because an ordinal element is exactly the set of its predecessors. Thus the ranges $\alpha$ and $\beta$ are equal.
