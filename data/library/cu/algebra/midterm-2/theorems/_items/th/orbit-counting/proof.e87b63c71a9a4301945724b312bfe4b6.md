Count the finite set $X=\{(g,a)\in G\times A:g\cdot a=a\}$. Counting first by $g$ gives $|X|=\sum_g|\operatorname{Fix}_A(g)|$. Counting by $a$ gives $|X|=\sum_a|G_a|$.

Within an orbit $O$, orbit–stabilizer gives $|G_a|=|G|/|O|$ for every $a\in O$. Hence

$$
\sum_{a\in O}|G_a|=|O|\frac{|G|}{|O|}=|G|.
$$

If there are $r$ orbits, summing yields $|X|=r|G|$. Equating the two counts proves the formula.

For a transitive action $r=1$, so $\sum_g|\operatorname{Fix}_A(g)|=|G|$. The identity contributes $|A|>1$. If every other element contributed at least one fixed point, the total would be at least $|A|+(|G|-1)>|G|$, a contradiction. Thus some element contributes zero.

**Scope:** this result supplies lecture context for the conjugate-union problem; the assigned solution of 4.3.24 uses the book's maximal-subgroup argument instead.
