**Subgroup implies equality.** Suppose $HK$ is a subgroup. Since it contains $H,K$, it contains $KH$. For $a\in HK$, its inverse belongs to $HK$, say $a^{-1}=hk$. Thus $a=k^{-1}h^{-1}\in KH$, proving the other inclusion.

**Equality implies subgroup.** If $HK=KH$, take $a=h_1k_1$, $b=h_2k_2$. Then $ab^{-1}=h_1(k_1k_2^{-1})h_2^{-1}$. Rewrite the middle product $(k_1k_2^{-1})h_2^{-1}$ as $h_3k_3$ using $KH=HK$. Hence $ab^{-1}=h_1h_3k_3\in HK$. The identity belongs to $HK$, so the subgroup test applies.

**Normalization implies equality.** If $hKh^{-1}=K$ for every $h\in H$, then $hk=(hkh^{-1})h\in KH$, giving $HK\subseteq KH$. Also $kh=h(h^{-1}kh)\in HK$, giving the reverse inclusion.

**Count the products.** Consider the surjection $H\times K\to HK$, $(h,k)\mapsto hk$. For a fixed expression $h_0k_0$, all its preimages are precisely

$$
(h_0t,t^{-1}k_0)\quad(t\in H\cap K).
$$

Indeed these pairs have the same product. Conversely if $hk=h_0k_0$, then $t=h_0^{-1}h=k_0k^{-1}$ belongs to $H\cap K$, and $h=h_0t,k=t^{-1}k_0$. Thus every fiber has $|H\cap K|$ elements. Counting gives $|H||K|=|HK||H\cap K|$, as claimed. This derivation requires no subgroup assumption on $HK$.

**Distinction:** $HK=KH$ is equality of sets; it does not say each $h$ commutes with each $k$.
