Let $f_1(x),f_2(x),\ldots,f_k(x)$ be @[polynomials]mt4-polynomial-ring with integer coefficients of the same degree $d$. Let $n_1,n_2,\ldots,n_k$ be integers which are @[relatively prime]math:num:divisibility:df:divisibility-gcd in pairs (i.e., $(n_i,n_j)=1$ for all $i\ne j$). Use the @[Chinese Remainder Theorem]mt4-chinese-remainder to prove there exists a polynomial $f(x)$ with integer coefficients and of degree $d$ with

$$
f(x)\equiv f_1(x)\bmod n_1,\qquad f(x)\equiv f_2(x)\bmod n_2,\qquad\ldots,\qquad f(x)\equiv f_k(x)\bmod n_k
$$

i.e., the coefficients of $f(x)$ agree with the coefficients of $f_i(x)\bmod n_i$. Show that if all the $f_i(x)$ are @[monic]mt4-polynomial-ring, then $f(x)$ may also be chosen monic. [Apply the Chinese Remainder Theorem in $\Z$ to each of the coefficients separately.]
