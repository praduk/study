**Existence by decreasing orders.** If $G=1$, use the empty series. Otherwise choose a maximal proper normal subgroup $M\nsubg G$. It exists because there are finitely many subgroups and at least the proper normal subgroup $1$. The quotient $G/M$ is nontrivial and simple: a nontrivial proper normal subgroup of it would pull back to a proper normal subgroup strictly between $M$ and $G$, contradicting maximality. Continue the same construction inside $M$. Each chosen subgroup has smaller finite order, so the process eventually reaches $1$. Read the chain upward to obtain a composition series.

**Uniqueness by induction on |G|.** The trivial group has only the empty series. Assume uniqueness for all groups of order smaller than $|G|$, and consider two composition series of $G$, with penultimate terms $A,B$. Each is a maximal proper normal subgroup of $G$: the corresponding top factor is simple, and subgroup correspondence forbids any proper intermediate normal subgroup.

If $A=B$, the portions of both series inside this same subgroup have the same factor multiset by induction. Adding the common final factor $G/A$ proves the result.

Now suppose $A\ne B$. Neither can contain the other, since both are maximal proper normal subgroups. The subgroup $AB$ is normal in $G$, because conjugation preserves both factors, and it strictly contains $A$. Hence $AB=G$. Let $D=A\cap B$, which is normal in $G$. The second isomorphism theorem gives

$$
A/D\cong G/B,\qquad B/D\cong G/A.
$$

Both quotients are nontrivial simple, so $D$ is a maximal proper normal subgroup of each of $A,B$.

Choose any composition series of $D$, whose existence was already proved. Appending $A$ to it gives a composition series of $A$, since its new top factor is $A/D$. Appending $B$ instead gives one of $B$ with top factor $B/D$. The induction hypothesis applies to $A$ and $B$ since both have smaller order than $G$. It says that the original first series below $G$ has, inside $A$, the factors of $D$ together with $A/D$, and the original second has, inside $B$, the factors of $D$ together with $B/D$.

Thus the factors of the first whole series are the factors of $D$, then $A/D$, then $G/A$. Those of the second are the factors of $D$, then $B/D$, then $G/B$. The two displayed isomorphisms identify the last two factors in opposite order. Therefore the multisets agree, including multiplicities, and their counts agree too. This completes the induction.

**What uniqueness does not mean.** It does not make the series itself unique or reconstruct $G$ from its factors. The assigned $Q_8,D_8$ examples have the same three $C_2$ factors but are different groups.
