**Strategy.** Adapt Euclid’s proof of infinitely many primes. Use one monic representative per associate class. From any proposed finite list, construct a polynomial with a prime factor outside the list.

**1. Choose representatives.** The @[polynomial units]mt4-polynomial-domains are the nonzero constants, so two nonzero polynomials are @[associates]mt4-associates exactly when one is a nonzero scalar multiple of the other. Dividing by the leading coefficient gives each class a unique @[monic]mt4-polynomial-ring representative. It suffices to find infinitely many monic primes.

**2. Force a prime factor.** Suppose $p_1,\ldots,p_k$ are all the monic primes. The list is nonempty since $x$ has a prime factor by @[unique factorization over a field]mt4-field-polynomial-pid-ufd. Form

$$
h=p_1\cdots p_k+1.
$$

Each $p_i$ has positive degree, so the product has positive degree by the @[degree formula]mt4-polynomial-domains. Adding $1$ leaves its leading term intact. Thus $h$ is a nonunit and has an @[irreducible factor]mt4-irreducible. In a UFD @[every irreducible is prime]mt4-irreducible-prime. Let $p$ be the monic associate of this factor.

**3. Rule out every listed prime.** If $p=p_i$, then $p$ divides both $h$ and $p_1\cdots p_k$, so it divides their difference $1$. That would make $p$ a unit, contrary to the @[definition of a prime element]mt4-prime-element. Hence the list misses $p$. This contradiction proves there are infinitely many pairwise nonassociate primes.
