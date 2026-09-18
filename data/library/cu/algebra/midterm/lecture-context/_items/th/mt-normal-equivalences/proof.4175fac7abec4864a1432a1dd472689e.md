Conjugation invariance is equivalent to $gH=Hg$ by multiplying the set equality on the right by $g$.
If $H$ is normal and representatives are $ah_1,bh_2$, then

$$
(ah_1)(bh_2)=ab(b^{-1}h_1b)h_2\in abH.
$$

Thus the product coset is independent of representatives; associativity, identity, and inverses follow from those in $G$. The projection $g\mapsto gH$ is a homomorphism with kernel $H$.
Conversely suppose the product rule is well-defined. For $h\in H$, equality $hH=H$ gives $(hH)(gH)=H(gH)$, hence $hgH=gH$ and $g^{-1}hg\in H$. This gives $g^{-1}Hg\subseteq H$ for every $g$; applying it to $g^{-1}$ and conjugating gives the reverse inclusion, so $H$ is normal.
Finally, if $H=\ker\varphi$, then $\varphi(ghg^{-1})=\varphi(g)1\varphi(g)^{-1}=1$, giving $gHg^{-1}\subseteq H$. Using $g^{-1}$ yields equality.
