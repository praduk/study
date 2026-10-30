**Order 48.** $n_2\mid3$, so $n_2=1$ or $3$. If $1$, the Sylow subgroup of order16 is normal. If $3$, then $3\not\equiv1\pmod4$ and the corollary gives $H=P\cap Q$ of order8. Its normalizer contains distinct order16 subgroups, so its order is a divisor of48, divisible by16, and larger than16: it must be48. Thus $H\trianglelefteq G$ and $G$ is not simple.

**Order 96.** The same argument gives $n_2=1$ or3. In the second case $|H|=16$; the only divisor of96 larger than32 and divisible by32 is96. Again $H\trianglelefteq G$. This is the model for the four-part mock.

**Order 80.** $n_2=1$ or5, and $5\equiv1\pmod4$; the index-2 corollary **does not apply**. But $5\not\equiv1\pmod8$: the generalized contrapositive gives a pair with intersection index2 or4. For $|P|=16$, this intersection is nontrivial. Choose an intersection $H$ of maximum order. By @mt3-max-intersection, $N_G(H)$ is not a 2-group, and its order is divisible by $2|H|$. Hence its order is20,40, or80 (depending on $H$). Index4 or2 produces a nontrivial proper kernel in a proposed simple order80 group, since $80\nmid4!$; order80 makes $H$ normal. The homework also gives a direct counting proof. **Knowing when the corollary fails is part of knowing it.**

**Generalized contrapositive.** If $n_p\not\equiv1\pmod{p^k}$, some distinct Sylow pair has index $p^j$ with $1\le j<k$. For $j>1$, do not assume that intersection is normal in either Sylow subgroup. Use a maximal intersection and its normalizer instead.

**Rapid checks, answer before reading:** Why does $n_2=3$ work but $n_2=5$ fail for the index-2 corollary? Which step uses the Sylow subgroups being $p$-groups? Why is an intersection of order1 useless for proving nonsimplicity? Why does the orbit proof sum over representatives?
