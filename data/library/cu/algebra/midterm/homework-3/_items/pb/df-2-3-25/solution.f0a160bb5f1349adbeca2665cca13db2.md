Choose integers $u,v$ with $ku+nv=1$ by Bézout's identity. In any finite group of order $n$, Lagrange's theorem applied to $\langle g\rangle$ gives $g^n=1$. Thus

$$
(g^u)^k=g^{uk}=g^{1-nv}=g.
$$

Every element has a $k$th root, proving the general assertion and hence the cyclic case. Alternatively, for $G=\langle a\rangle$, $a^k$ is a generator because $|a^k|=n/\gcd(n,k)=n$.
The inverse function is $g\mapsto g^u$, so the power map is in fact bijective. In a nonabelian group it need not be a homomorphism; no such claim was used.

**Technique:** use Bézout to invert an exponent modulo the group order, then apply Lagrange element by element.
