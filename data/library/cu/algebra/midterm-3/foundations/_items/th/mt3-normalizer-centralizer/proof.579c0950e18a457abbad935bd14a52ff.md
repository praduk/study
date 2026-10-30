Clearly $C_G(H) \subg N_G(H)$.  To show $C_G(H) \nsubg N_G(H)$, let $c\in C_G(H)$ and $g\in N_G(H)$.  We need to show $gcg^{-1}\in C_G(H)$.  We know that
$$
chc^{-1}\in H.
$$
So try conjugating by $gcg^{-1}$
$$
(gcg^{-1}) h (gc^{-1}g^{-1}).
$$
Because $g$ is in the normalier of $H$, there exists a $h'=g^{-1}hg\in H$ so that
$$
(gcg^{-1}) h (gc^{-1}g^{-1}) = gch'c^{-1}g^{-1} = gh'g^{-1} = h.
$$


By @mt3-normalizer, conjugation by $g\in N_G(H)$ is an automorphism of $H$. The map sending $g$ to this automorphism is a homomorphism because conjugations compose in the same order. Its kernel is precisely @mt3-centralizer. Now apply @mt3-first-isomorphism. **Use when:** normality lets you turn conjugation into a homomorphism with a known finite target order.
