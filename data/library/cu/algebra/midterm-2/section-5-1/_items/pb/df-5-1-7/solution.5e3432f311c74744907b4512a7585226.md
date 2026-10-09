**Step 1: check the codomain.** For each position $j$, the output coordinate is $g_{\pi^{-1}(j)}\in G_{\pi^{-1}(j)}$. It therefore belongs to the prescribed factor in that position, making the map well defined even when the groups differ.

**Step 2: preserve multiplication.** Products in a direct product are coordinatewise. For tuples $g=(g_i)$ and $h=(h_i)$, the $j$th coordinate of $\varphi_\pi(gh)$ is $g_{\pi^{-1}(j)}h_{\pi^{-1}(j)}$. This is also the $j$th coordinate of $\varphi_\pi(g)\varphi_\pi(h)$. Equality in every coordinate proves the homomorphism property.

**Step 3: construct the inverse.** For a target tuple $k=(k_1,\ldots,k_n)$, define

$$
\psi(k)=(k_{\pi(1)},\ldots,k_{\pi(n)}).
$$

The $i$th coordinate lies in $G_i$, since $k_{\pi(i)}\in G_{\pi^{-1}(\pi(i))}=G_i$. Then

$$
(\psi\varphi_\pi(g))_i=g_{\pi^{-1}(\pi(i))}=g_i,
$$

and

$$
(\varphi_\pi\psi(k))_j=k_{\pi(\pi^{-1}(j))}=k_j.
$$

Thus $\psi$ is a two-sided inverse, so $\varphi_\pi$ is bijective and hence an isomorphism.

**Technique:** check a tuple map one coordinate at a time. The inverse indices ensure that the map goes to the stated reordered product.

**Foundations:** @cu:algebra:midterm-2:definitions:df:product-complement-minimal.
