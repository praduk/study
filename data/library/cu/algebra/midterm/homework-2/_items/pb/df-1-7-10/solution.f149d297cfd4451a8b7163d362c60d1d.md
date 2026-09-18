(a) If $1\le k<n$ and $\sigma(i)=j\ne i$, choose a $k$-element subset containing $i$ but not $j$: choose the other $k-1$ elements from the remaining $n-2$. Its image contains $j$, so it is moved. Hence only the identity fixes every subset.
If $k=n$, there is just one subset, so the kernel is all of $S_n$. This action is not faithful for $n\ge2$, but is faithful for $n=1$ because $S_1$ is trivial.

(b) For every allowed $k\ge1$ the action is faithful: if $\sigma(i)\ne i$, any tuple with first coordinate $i$ is moved. This argument also works if the convention requires distinct coordinates, because $k\le n$ lets us complete such a tuple.

**Technique:** to prove faithfulness, take an arbitrary nonidentity permutation and construct an object it moves. Preserve the trivial-group boundary case.
