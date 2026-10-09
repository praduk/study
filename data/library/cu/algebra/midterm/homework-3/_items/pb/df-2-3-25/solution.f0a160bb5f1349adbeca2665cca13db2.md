Let $G$ be cyclic of finite order $n$ and let $k\in\Z$ satisfy $\gcd(k,n)=1$. Prove that $x\mapsto x^k$ is surjective. Then use Lagrange’s theorem to prove the same result for any finite group of order $n$.

(a) Let $G$ be cyclic of finite order.  Let $G=\genby{x}$.  We have that
$$
|x^k| = \frac{|x|}{\gcd(|x|,k)} = |x| = |G|.
$$

So $|\genby{x^k}|=|G|$  therefore the map $x\mapsto x^k$ is surjective.

(b) Let $G$ be a finite group of order $n$.  Let $x\in G$.  Then $|x|$ divides
$|G|$ by Lagrange.  Let
$$
c = \frac{|G|}{|x|}.
$$

We have
$$
\gcd(k,|G|) = 1 \iff \exists a,b\in \, 1 = ak + b|G| = ak + bc|x| \iff \gcd(k,|x|)=1.
$$

Let $g\in G$.  Define $\Psi_g:\genby{g}\to\genby{g}$ map $x\mapsto x^k$.  By (a) $\Psi_g$ is surjective.  So there exists a $z=\Psi_y^{-1}(g)\in G$ so that $z^k = g$.
