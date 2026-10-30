**Tools used:** @mt3-lagrange, @mt3-cauchy, and @mt3-subgroup-product; Bézout’s identity for integers says that integers with greatest common divisor $1$ have an integer linear combination equal to $1$. We use additive notation in the cyclic-factor splitting step.

For $A=1$, use the empty product. Assume henceforth that $A$ is nontrivial.

First split $A$ into its primary components without using Sylow theory. Write $|A|=\prod_p p^{a_p}$ and put $A_p=\{x\in A:x^{p^{a_p}}=1\}$. These are subgroups because $A$ is abelian. Each $A_p$ has prime-power order: if a different prime divided its order, Cauchy would produce an element of that prime order, contradicting its defining exponent condition. The integers $|A|/p^{a_p}$ have greatest common divisor $1$, so choose integers $e_p$, each divisible by $|A|/p^{a_p}$, with $\sum_p e_p=1$. Then $x=\prod_p x^{e_p}$ and each $x^{e_p}$ belongs to $A_p$ by Lagrange. The product is direct: an element in one $A_p$ and the product of the other components has order both a power of $p$ and prime to $p$, so is $1$. It remains to split an abelian $p$-group $A$.

For $A\ne1$, choose an element $x$ of maximum order $p^a$. Then $p^aA=0$. Start with $f:\langle x\rangle\to\Z/p^a\Z$ sending $x$ to $1$. We can extend $f$ from any subgroup $B$ containing $x$ to a larger subgroup unless $B=A$. Choose $y\notin B$, with $y+B$ of order $p^k$, where $1\le k\le a$. The element $p^ky$ has order dividing $p^{a-k}$, so its image under $f$ lies in $p^k(\Z/p^a\Z)$. Choose $t$ with $p^kt=f(p^ky)$ and set

$$
f(b+iy)=f(b)+it.
$$

If $b+iy=b'+jy$, then $i-j$ is a multiple of $p^k$; the displayed choice of $t$ proves the two values equal. Thus the extension is well defined. Finiteness allows iteration until $f:A\to\Z/p^a\Z$ is defined. Its restriction to $\langle x\rangle$ is an isomorphism, giving $A=\langle x\rangle\oplus\ker f$. Induct on $|A|$ to obtain cyclic prime-power factors.

For uniqueness, if $A=\prod_i C_{p^{a_i}}$, the number killed by $p^k$ is $p^{d_k}$, where $d_k=\sum_i\min(k,a_i)$. Thus $d_k-d_{k-1}$ is the number of exponents $a_i\ge k$, recovering the complete multiset of exponents from $A$. Finally order the exponents for each prime decreasingly, pad with zeros, and combine corresponding coprime factors; $C_m\times C_n\cong C_{mn}$ for coprime $m,n$ because the pair of generators has order $mn$. This gives the asserted invariant factors and their uniqueness.
