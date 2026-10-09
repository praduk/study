Let $G$ be a finite group and let $H\le G$. Consider the action of $H$ on $G$ by left multiplication:
$$
h\cdot x=hx.
$$
The orbit of $x\in G$ is
$$
Hx=\{hx:h\in H\}.
$$

**1. Belonging to the same orbit is an equivalence relation.**

For $x,y\in G$, define
$$
x\sim y
\iff x=hy\text{ for some }h\in H.
$$
Since $x=hy$ is equivalent to $xy^{-1}=h$, we have
$$
x\sim y\iff xy^{-1}\in H.
$$

We verify the three properties of an equivalence relation.

**Reflexivity.** For every $x\in G$,
$$
xx^{-1}=e\in H,
$$
so $x\sim x$.

**Symmetry.** Suppose $x\sim y$. Then $xy^{-1}\in H$. Since $H$ is closed under inverses,
$$
yx^{-1}=(xy^{-1})^{-1}\in H.
$$
Thus $y\sim x$.

**Transitivity.** Suppose $x\sim y$ and $y\sim z$. Then $xy^{-1}\in H$ and $yz^{-1}\in H$. Since $H$ is closed under multiplication,
$$
(xy^{-1})(yz^{-1})
=x(y^{-1}y)z^{-1}
=xz^{-1}\in H.
$$
Thus $x\sim z$.

Therefore $\sim$ is an equivalence relation on $G$.

**2. Two elements are equivalent exactly when their orbits are equal.**

Suppose $x\sim y$. Then $x=hy$ for some $h\in H$. For every $a\in H$,
$$
ax=a(hy)=(ah)y\in Hy,
$$
because $ah\in H$. Hence $Hx\subseteq Hy$.

Also, $y=h^{-1}x$, so for every $a\in H$,
$$
ay=a(h^{-1}x)=(ah^{-1})x\in Hx.
$$
Hence $Hy\subseteq Hx$, proving $Hx=Hy$.

Conversely, suppose $Hx=Hy$. Since $e\in H$, we have
$$
x=ex\in Hx=Hy.
$$
Thus $x=hy$ for some $h\in H$, so $x\sim y$.

Consequently,
$$
\boxed{x\sim y\iff Hx=Hy\iff xy^{-1}\in H.}
$$

The equivalence class of $x$ is precisely its orbit:
$$
[x]
=\{y\in G:y\sim x\}
=\{y\in G:yx^{-1}\in H\}
=\{hx:h\in H\}
=Hx.
$$

**3. The orbits partition $G$.**

Every $x\in G$ lies in its own orbit, because $x=ex\in Hx$. Thus the orbits cover $G$.

Now suppose two orbits $Hx$ and $Hy$ intersect. Choose
$$
z\in Hx\cap Hy.
$$
Then $z\sim x$ and $z\sim y$. By symmetry, $x\sim z$, and by transitivity, $x\sim y$. Therefore $Hx=Hy$.

Thus any two orbits are either equal or disjoint, so the distinct orbits partition $G$.

**4. Every orbit has $|H|$ elements.**

For each $x\in G$, define
$$
\varphi_x:H\longrightarrow Hx,
\qquad
\varphi_x(h)=hx.
$$
This map is surjective because every element of $Hx$ has the form $hx$ for some $h\in H$.

To prove injectivity, suppose
$$
\varphi_x(h_1)=\varphi_x(h_2).
$$
Then $h_1x=h_2x$. Multiplying both sides on the right by $x^{-1}$ gives
$$
h_1=h_2.
$$
Therefore $\varphi_x$ is a bijection, and
$$
|Hx|=|H|.
$$

**5. Count the elements of $G$.**

Since $G$ is finite, there are finitely many distinct orbits. Write them as
$$
Hx_1,\ldots,Hx_t.
$$
These orbits partition $G$, and each contains $|H|$ elements. Hence
$$
|G|
=\sum_{i=1}^{t}|Hx_i|
=\sum_{i=1}^{t}|H|
=t|H|.
$$
Therefore
$$
\boxed{|H|\mid |G|.}
$$

The sets $Hx$ are **right cosets**, even though the action is by left multiplication: the representative $x$ appears to the right of $H$. No normality assumption is needed.

**Technique:** construct a partition into equally sized pieces, prove their sizes using explicit bijections, and count.
