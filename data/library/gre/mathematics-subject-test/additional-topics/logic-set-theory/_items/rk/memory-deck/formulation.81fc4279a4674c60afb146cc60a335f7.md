## Logic

$P\Rightarrow Q$ is equivalent to $\neg Q\Rightarrow\neg P$, not to its converse. Also

$$
P\Rightarrow Q\equiv\neg P\lor Q.
$$

De Morgan and quantifier negation:

$$
\neg(P\land Q)\equiv\neg P\lor\neg Q,
\quad
\neg(P\lor Q)\equiv\neg P\land\neg Q,
$$

$$
\neg\forall x\,P(x)\equiv\exists x\,\neg P(x),
\quad
\neg\exists x\,P(x)\equiv\forall x\,\neg P(x).
$$

When negating nested statements, reverse every quantifier and negate the final predicate.

## Sets, functions, and relations

$$
(A\cup B)^c=A^c\cap B^c,\qquad
(A\cap B)^c=A^c\cup B^c.
$$

For finite $A$, $|\mathcal P(A)|=2^{|A|}$. A function $A\to B$ is injective when equal outputs force equal inputs, surjective when every element of $B$ is hit, and bijective when both.

For $|A|=m$ and $|B|=n$, there are $n^m$ functions $A\to B$ and

$$
n(n-1)\cdots(n-m+1)
$$

injections when $m\le n$.

An equivalence relation is reflexive, symmetric, and transitive. Its equivalence classes partition the set, and every partition determines an equivalence relation.

A partial order is reflexive, antisymmetric, and transitive. Do not confuse antisymmetric with "not symmetric."

## Cardinality

A set is countable if it is finite or bijective with a subset of $\mathbb N$. Countable unions of countable sets are countable. $\mathbb Z$ and $\mathbb Q$ are countable; $\mathbb R$ and $\mathcal P(\mathbb N)$ are uncountable. Cantor's theorem gives

$$
|A|<|\mathcal P(A)|.
$$

Use Cantor-Bernstein when injections exist in both directions.

## Proof triggers

Use contrapositive for divisibility implications, contradiction for impossibility or irrationality, induction for recursively built integer statements, and a counterexample to disprove a universal claim. One example never proves a universal statement.
