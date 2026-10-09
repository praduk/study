Use the set of tuples $S=\{(x_1,\ldots,x_p):x_1\cdots x_p=1\}$. Its first $p-1$ entries are arbitrary and determine the last, so $|S|=|G|^{p-1}$ is divisible by $p$.

Cyclic rotation preserves $S$: $x_2\cdots x_px_1=x_1^{-1}(x_1\cdots x_p)x_1=1$. The cyclic group of order $p$ therefore acts on $S$. Every orbit has size $1$ or $p$, by orbit–stabilizer and primality. A singleton is exactly a constant tuple $(x,\ldots,x)$ with $x^p=1$.

Let $k$ count those singletons. Counting the other orbits in multiples of $p$ gives $k\equiv|S|\equiv0\pmod p$. The identity tuple shows $k\ge1$, so $k\ge p>1$. Another singleton therefore gives $x\ne1$ with $x^p=1$. Its order divides $p$ and is not $1$, hence is $p$.

The six-part assigned exercise supplies every detail of this argument: @cu:algebra:midterm-2:section-3-2:pb:df-3-2-9:sl. There is no commutativity assumption.
