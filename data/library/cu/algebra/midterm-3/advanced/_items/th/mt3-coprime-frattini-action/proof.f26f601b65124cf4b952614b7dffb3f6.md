**Results used:** @mt3-frattini, @mt3-frattini-nongenerators, @mt3-fixed-points, @mt3-linear-automorphisms.

First suppose an automorphism $\beta$ of prime order $q\ne p$ acts trivially on $P/\Phi(P)$. Each coset is $\beta$-invariant because $\Phi(P)$ is characteristic. Its size is a power of $p$, so is not divisible by $q$. The orbits of $\langle\beta\rangle$ have size $1$ or $q$; each coset therefore has a fixed representative. Choose a fixed representative for each vector of a quotient basis. These representatives generate $P$ by Burnside's basis theorem, so $\beta$ fixes all of $P$, contradiction.

If a nonidentity automorphism $\alpha$ of coprime order $m$ induced the identity, choose a prime $q\mid m$. Then $\alpha^{m/q}$ has prime order $q\ne p$ and induces the identity, contradicting the first case. Finally restrict $\Aut(P)\to\Aut(P/\Phi(P))$ to $A$. Every element of its kernel has order prime to $p$, hence is the identity. This proves injectivity and the claimed embedding.
