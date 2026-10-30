Given groups $N,H$ and a homomorphism $\varphi:H\to\Aut(N)$, the **external semidirect product** $N\semid_\varphi H$ has underlying set $N\times H$ and operation

$$
(n,h)(m,k)=(n\varphi(h)(m),hk).
$$

Its identity is $(1,1)$ and $(n,h)^{-1}=(\varphi(h^{-1})(n^{-1}),h^{-1})$. The factor $N$ is normal, the factors intersect in1, and the quotient by $N$ is $H$. The action is trivial iff these embedded factors commute, giving the direct product with these factors.

**Internal recognition.** If $N\trianglelefteq G$, $H\le G$, $N\cap H=1$, and $NH=G$, then $G\cong N\semid H$, with $h\cdot n=hnh^{-1}$. Such an $H$ is a **complement** to $N$. Finite coprime orders give trivial intersection; still check normality and that the product has full order. A quotient $G/N\cong H$ alone does not supply a complement (e.g. $C_4$ over its order2 subgroup).

**Action first.** State which factor is normal and the map into its automorphism group. The course also uses $H\semidop N$ for the same convention. Do not infer direction from the English phrase “semidirect product of.”

**Cyclic actions.** $\Aut(C_n)\cong(\Z/n\Z)^\times$: an automorphism sends a generator $a$ to $a^u$ with $\gcd(u,n)=1$. An action of $C_m=\langle b\rangle$ is specified by such a $u$ satisfying $u^m\equiv1\pmod n$. Its presentation is

$$
\langle a,b\mid a^n=b^m=1,\ bab^{-1}=a^u\rangle.
$$

**Wreath product needed for HW1.** $G\wr S_n=G^n\semid S_n$, where $\sigma$ acts on $(g_1,\ldots,g_n)$ by $(g_{\sigma^{-1}(1)},\ldots,g_{\sigma^{-1}(n)})$. The inverse in the indices makes this a left action. For $C_2\wr S_n$, view elements as signed permutation matrices.
