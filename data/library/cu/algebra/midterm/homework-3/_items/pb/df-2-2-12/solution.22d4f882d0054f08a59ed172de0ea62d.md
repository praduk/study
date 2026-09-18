(a) Substitute indices, then commute the variables into increasing index order:

$$
\begin{aligned}
\sigma\cdot p&=12x_1x_2^5x_3^7-18x_3^3x_4+11x_1^{23}x_2^6x_3x_4^3,\\
\tau\cdot(\sigma\cdot p)&=12x_1^7x_2x_3^5-18x_1^3x_4+11x_1x_2^{23}x_3^6x_4^3.
\end{aligned}
$$

Since $\tau\sigma=(1\ 3\ 4\ 2)$, $(\tau\sigma)\cdot p$ is the second displayed polynomial. Since $\sigma\tau=(1\ 3\ 2\ 4)$,

$$
(\sigma\tau)\cdot p=12x_1x_3^5x_4^7-18x_2x_4^3+11x_1^{23}x_2^3x_3^6x_4.
$$

(b) The identity fixes each variable. Applying $\beta$ and then $\alpha$ sends $x_i$ to $x_{\alpha(\beta(i))}$. The same equality extends to each monomial and sum, so $\alpha\cdot(\beta\cdot p)=(\alpha\beta)\cdot p$. Each substitution stays in $R$ and is invertible using the inverse permutation.

(c) A permutation fixes $x_4$ exactly when it fixes the index $4$. The stabilizer is $\{1,(12),(13),(23),(123),(132)\}$. Restriction to $\{1,2,3\}$ is a bijective homomorphism onto $S_3$.

(d) The stabilizer preserves $\{1,2\}$ and its complement setwise, so it is $\{1,(12),(34),(12)(34)\}\cong C_2\times C_2$. These four permutations commute.

(e) Independence of the monomials means the unordered pair of blocks $\{\{1,2\},\{3,4\}\}$ must be preserved. There are $2\cdot2\cdot2=8$ possibilities, namely

$$
\begin{gathered}1,(12),(34),(12)(34),\\(13)(24),(14)(23),(1324),(1423).\end{gathered}
$$

Take $r=(1324)$ and $s=(12)$. They preserve the blocks as a pair, $r$ has order four, $s$ has order two, and conjugating the cycle gives $srs=r^{-1}$. The eight elements $r^i,sr^i$ are distinct: $s\notin\langle r\rangle$, and each coset has four elements. Thus they exhaust the stabilizer and give an isomorphism from $D_8$.

(f) Expanding gives the sum of the four cross-block monomials $x_1x_3,x_1x_4,x_2x_3,x_2x_4$. A permutation preserves this set exactly when it preserves the complementary set of two square-free quadratic monomials $\{x_1x_2,x_3x_4\}$. This is exactly the condition in (e).

**Technique:** interpret a stabilizer as preservation of a combinatorial structure; use independent monomials to prove completeness; check a presentation and count to establish an isomorphism.
