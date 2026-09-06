**Correct choice: (B).**

**Fastest valid route.** Expand the inclusion elementwise:

$$
A\subseteq\bigcup_{n=1}^{\infty}B_n
\quad\Longleftrightarrow\quad
\forall x\,[x\in A\Rightarrow\exists n\ge1\ (x\in B_n)].
$$

Negation produces one element of $A$ that belongs to none of the $B_n$.

**Verification.** Negating the displayed quantified implication gives

$$
\exists x\,[x\in A\land\neg\exists n\ge1\ (x\in B_n)]
\quad\Longleftrightarrow\quad
\exists x\in A\;\forall n\ge1,\ x\notin B_n.
$$

Choices (C) and (D) allow the missing element to depend on a selected set or on $n$; neither requires one element to be absent from every $B_n$.
