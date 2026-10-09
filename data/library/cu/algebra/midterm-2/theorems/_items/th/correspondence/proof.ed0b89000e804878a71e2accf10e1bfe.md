**The constructions give subgroups.** Images and preimages of subgroups under homomorphisms are subgroups: the subgroup test follows by applying the map to $ab^{-1}$. The preimage always contains $N$, because $N$ maps to the identity.

**The constructions are inverse.** For $N\le H$, an element $g$ belongs to $\pi^{-1}(\pi(H))$ exactly when $gN=hN$ for some $h\in H$. Then $h^{-1}g\in N\le H$, so $g\in H$. The reverse inclusion is immediate. Conversely, since $\pi$ is onto, every point of a subgroup $\bar H\le G/N$ has a preimage, so $\pi(\pi^{-1}(\bar H))=\bar H$.

**Inclusion and intersections.** Inclusion is preserved by images and preimages. If $H,K$ contain $N$, then $gN\in(H/N)\cap(K/N)$ implies $g\in H\cap K$ by the inverse property, proving $(H\cap K)/N=(H/N)\cap(K/N)$. The reverse inclusion is also direct.

**Joins.** The image under a homomorphism of a word in elements of $H,K$ is the corresponding word in their images. Conversely any word in the images lifts to that word in $H,K$. Hence $\pi(\langle H,K\rangle)=\langle\pi(H),\pi(K)\rangle$.

**Indices.** For $N\le H\le K$, the map from left $H$-cosets in $K$ to left $H/N$-cosets in $K/N$, given by $kH\mapsto(kN)(H/N)$, is a bijection: equality of the target cosets says $\pi(k'^{-1}k)\in H/N$, equivalently $k'^{-1}k\in H$. Surjectivity follows from surjectivity of $K\to K/N$. Therefore $[K:H]=[K/N:H/N]$.

**Normality.** If $H\nsubg K$, conjugation by $kN$ sends $H/N$ to itself. Conversely normality of $H/N$ in $K/N$ implies $\pi(khk^{-1})\in H/N$ for $k\in K,h\in H$, so $khk^{-1}\in H$. Applying the statement to $k^{-1}$ gives equality. Finally, the map $K/N\to K/H$, $kN\mapsto kH$, is well defined, onto, and has kernel $H/N$, so the First Isomorphism Theorem gives the last assertion.
