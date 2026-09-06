## Decide the model before calculating

Ask: does order matter, is repetition allowed, are objects distinct, and are rotations or reflections identified?

$$
P(n,k)=\frac{n!}{(n-k)!},\qquad
\binom nk=\frac{n!}{k!(n-k)!}.
$$

Repeated-type permutations number $n!/(n_1!\cdots n_k!)$. Circular arrangements of $n$ distinct labeled objects up to rotation number $(n-1)!$; if reflections are also identified, additional symmetry analysis is required.

## Binomial and multinomial tools

$$
(x+y)^n=\sum_{k=0}^n\binom nkx^{n-k}y^k,
$$

$$
\binom nk=\binom{n-1}k+\binom{n-1}{k-1}.
$$

The coefficient of $x^n$ in a product of generating functions counts selections whose encoded total is $n$.

## Stars and bars

Nonnegative solutions of $x_1+\cdots+x_k=n$:

$$
\binom{n+k-1}{k-1}.
$$

Positive solutions:

$$
\binom{n-1}{k-1}.
$$

Upper bounds are not handled by plain stars and bars; use inclusion-exclusion, complements, or generating functions.

## Inclusion-exclusion and surjections

$$
\left|\bigcup_iA_i\right|=
\sum|A_i|-\sum|A_i\cap A_j|+\sum|A_i\cap A_j\cap A_k|-\cdots.
$$

The number of onto functions from an $n$-element set to a $k$-element set is

$$
\sum_{j=0}^k(-1)^j\binom kj(k-j)^n.
$$

Derangements satisfy

$$
!n=n!\sum_{j=0}^n\frac{(-1)^j}{j!}.
$$

## Pigeonhole, recurrences, and generating functions

Putting $N$ objects into $k$ boxes forces some box to contain at least $\lceil N/k\rceil$ objects.

For a linear recurrence, try $a_n=r^n$. A repeated characteristic root $r$ produces terms $n^jr^n$. Ordinary generating functions turn convolution and recurrence shifts into algebra.

## Trap list

Do not divide by $k!$ unless order truly became irrelevant, do not apply $(n-1)!$ to necklaces with repeated colors, and do not subtract forbidden cases without repairing overlaps.
