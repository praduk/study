Consider the tuples $(x_1,\ldots,x_p)\in G^p$ satisfying $x_1\cdots x_p=1$. There are $|G|^{p-1}$ tuples, because the first $p-1$ determine the last. Cyclic rotation preserves this set: $x_2\cdots x_px_1=x_1^{-1}(x_1\cdots x_p)x_1=1$.

Each rotation orbit has size $1$ or $p$. The fixed tuples are $(x,\ldots,x)$ with $x^p=1$, so the number of such $x$ is congruent to $|G|^{p-1}=0$ modulo $p$. One is the identity, hence there is a nonidentity one. Its order divides $p$ and is therefore $p$. This elementary orbit count is the mechanism behind @mt3-fixed-points.
