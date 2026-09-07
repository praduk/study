For functors $F,G:\mathcal C\to\mathcal D$, a natural transformation $\alpha:F\Rightarrow G$ consists of morphisms $\alpha_A:FA\to GA$ such that for every $f:A\to B$,

$$
G(f)\alpha_A=\alpha_BF(f).
$$

This equation is the naturality square. Its components are not arbitrary unrelated maps: they must respect every arrow in the source category. Vertical composition is pointwise: $(\beta\alpha)_A=\beta_A\alpha_A$. Identity components define the identity natural transformation.
