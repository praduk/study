## Core facts

Use the sum rule for disjoint alternatives and the product rule for sequential choices. There are $n!$ permutations of $n$ distinct objects, $n!/(n_1!\cdots n_k!)$ permutations with repeated types, and $\binom nk$ unordered $k$-subsets. For ordered samples, decide whether repetition is allowed before writing a power or falling factorial.

Stars and bars counts nonnegative integer solutions of

$$
x_1+\cdots+x_k=n
$$

as $\binom{n+k-1}{k-1}$. Positive solutions reduce to nonnegative ones by setting $y_i=x_i-1$. Upper bounds require inclusion-exclusion, generating functions, or a complement substitution; plain stars and bars does not enforce caps.

Inclusion-exclusion for three sets begins

$$
|A\cup B\cup C|=|A|+|B|+|C|-|A\cap B|-|A\cap C|-|B\cap C|+|A\cap B\cap C|.
$$

The number of onto functions from an $n$-element set to a $k$-element set is

$$
\sum_{j=0}^{k}(-1)^j\binom kj(k-j)^n.
$$

The pigeonhole principle forces some box to contain at least $\lceil n/k\rceil$ objects when $n$ objects enter $k$ boxes. Binomial and multinomial expansions encode selection counts. The coefficient of $x^n$ in a product of generating functions counts ways to obtain total $n$ subject to the choices represented by each factor.

Linear recurrences are solved from their characteristic roots, with repeated roots gaining powers of $n$. Combinatorial proofs establish identities by counting the same set in two ways. For circular arrangements of distinct objects, rotations usually identify arrangements, giving $(n-1)!$ before any reflection symmetry is imposed.

## Recognition cues

- Write down what is labeled, what is identical, whether order matters, and whether repetition is allowed.
- For “at least one,” the complement is often faster.
- For “onto” or “none empty,” expect inclusion-exclusion.
- For small remaining distance from a maximum, complement each bounded variable.

## Edge cases and traps

- Dividing by $k!$ is valid only when every unordered outcome was counted exactly $k!$ times.
- Stars and bars distinguishes boxes; it does not distinguish identical objects.
- Inclusion-exclusion signs alternate and intersections are added back at the next level.
- Circular arrangements with reflections identified require an additional symmetry analysis; blindly dividing by two can fail when stabilizers occur.
- Check whether endpoints, empty selections, and zero parts are permitted.
