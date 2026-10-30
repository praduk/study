Suppose $G$ acts transitively on a finite nonempty set $A$, and $H\nsubg G$. Let $O_1,\ldots,O_r$ be the $H$-orbits.

## Prove $G$ permutes the $H$-orbits transitively, and all have equal cardinality.
$G$, a finite group acts on $A$ transitively.  $H\nsubg G$.  Let $a\in A$ and $g\in G$.

Then
$$
g H \cdot a = gHg^{-1} \cdot g \cdot a = H \cdot (g\cdot a).
$$

So $g$ takes $\Orb_H(a)$ to $\Orb_H(g\cdot a)$.

This defines a $G$-action on the collection of orbits. Given $O_i,O_j$, choose $a_i\in O_i,a_j\in O_j$. Transitivity on $A$ gives that there exists a $g$ so that $g\cdot a_i=a_j$. Then $gO_i=O_j$. Hence the action on the orbit collection is transitive.

Define $\phi_g: A\to A$ mapping $a\mapsto g\cdot a$.  $\phi_g$ is a bijectin of $A$ because $g$ is a group action and has an inverse action $\phi_{g^{-1}}$.

$\phi_g$ maps $O_i$ to $O_j$.  The map is injective on this restriction and so it is bijective proving equal sizes.

## For $a\in O_1$, prove $|O_1|=[H:H\cap G_a]$ and $r=[G:HG_a]$.

Let $a\in O_1$ and let $G$ act on the orbits $H\cdot a = O_a$.  By Orbit-stabilizer
$$
|O_a|=|\Orb_H(a)|=[H:\Stab_H(a)].
$$

But notice that $\Stab_H(a)=H\cap \Stab_G(a)$.  So
$$
|O_a|=|\Orb_H(a)|=[H:H\cap \Stab_G(a)].
$$

Let $G$ act on the orbits $O_i$.  Then
$$
r = |\Orb_G(O_1)| = [G:\Stab_G(O_1)].
$$
Note that
$$
\Stab_G(O_1) = \set{g\in G : g\cdot a \in O_1} = H \Stab_G(a).
$$
So,
$$
r = [G:H\Stab_G(a)].
$$
