Direct replacement would give $∃y(R(y,y)∧∀zS(y,z))$, in which the inserted occurrence of $y$ is captured by $∃y$. It changes the intended dependence and is not substitution.

Choose a fresh variable, say $w$, and first alpha-rename the bound $y$: $∃w(R(x,w)∧∀zS(w,z))$. Now replace the free $x$ by $y$, obtaining $∃w(R(y,w)∧∀zS(w,z))$. The inserted $y$ remains free, as required.
