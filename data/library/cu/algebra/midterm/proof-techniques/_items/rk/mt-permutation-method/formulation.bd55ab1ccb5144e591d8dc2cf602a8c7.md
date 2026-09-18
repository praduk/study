**Use when:** computing products, listing possible orders, or finding a finite stabilizer.

For a product, apply the rightmost permutation first. Trace the least unused symbol until it returns; repeat until every symbol is accounted for. For possible orders in $S_n$, enumerate all partitions of $n$ and take the least common multiple of each cycle type. Provide a witness for each order and use the exhaustive partition list to exclude all others.

For a stabilizer, identify what structure must be preserved. In 2.2.12(e), the structure is a partition into two unordered blocks, giving $2!\,2!\,2!=8$ permutations. Equality of polynomials is checked by coefficients of independent monomials.

**Assigned uses:** 1.3.1, 6, 18; 1.7.8(b); 2.2.6(a), 12.

**Common failure:** merely exhibiting several examples does not prove a complete list. Cycle rotation duplicates the same cycle, but reversing a cycle usually changes it.
