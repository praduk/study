Induct on terms. Variables and constants use the definition of assignment and preservation of constants. The function step uses $F(f^𝔐(\bar a))=f^𝔑(F\bar a)$.

Induct on formulas. For relations, use preservation and reflection of $R$ by the bijection $F$ together with the term result. Equality is preserved and reflected because $F$ is injective. Boolean cases are truth-functional. For $∀xφ$, each $b∈N$ has a unique form $F(a)$ because $F$ is onto, and $(F∘g)[x↦F(a)]=F∘(g[x↦a])$; apply the induction hypothesis for all $a$. The existential case uses the same correspondence of witnesses.
