## Core facts

- A group has an associative operation, identity, and inverses. For a nonempty subset $H\subseteq G$, the one-step subgroup test $ab^{-1}\in H$ for all $a,b\in H$ is often fastest.
- In a cyclic group of order $n$, there is one subgroup for each divisor $d$ of $n$, and exactly $\varphi(d)$ elements of order $d$. The order of $g^k$ is $n/\gcd(n,k)$ when $g$ has order $n$.
- Lagrange gives $|G|=[G:H]|H|$ for finite $G$. Element orders and subgroup orders divide $|G|$, but the converses need not hold without extra hypotheses.
- Left cosets partition $G$. A subgroup is normal exactly when left and right cosets agree; kernels are always normal, and quotient groups require normality.
- For a homomorphism $\phi$, use $G/\ker\phi\cong\operatorname{im}\phi$ and, in the finite case, $|G|=|\ker\phi|\,|\operatorname{im}\phi|$.
- In permutation groups, compose in the stated order, decompose into disjoint cycles, and use the least common multiple of cycle lengths for the order.

## Recognition cues and traps

List a few powers before invoking heavy theory in a small cyclic or permutation group. For maps between quotient groups, check well-definedness before computing a kernel. Do not assume every subgroup is normal or cancel elements across a noncommutative product as though order did not matter.
