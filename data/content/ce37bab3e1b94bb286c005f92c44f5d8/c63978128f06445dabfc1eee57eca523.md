A **uniform substitution** is a function $\sigma:\mathsf{Prop}\to\mathsf{Form}$. It extends uniquely to formulas by

$$p\sigma=\sigma(p),\quad \true\sigma=\true,\quad \false\sigma=\false,$$

$$(\neg A)\sigma=\neg(A\sigma),\qquad (A\circ B)\sigma=(A\sigma)\circ(B\sigma).$$

Every occurrence of the same atom is replaced by the same formula, simultaneously. Substitution is syntactic; it does not assign truth values.
