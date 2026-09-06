A **valuation** is a function $v:\mathsf{Prop}\to\{0,1\}$. Its unique recursive extension $\llbracket\cdot\rrbracket_v:\mathsf{Form}\to\{0,1\}$ is given by

$$\llbracket\true\rrbracket_v=1,\qquad \llbracket\false\rrbracket_v=0,$$

$$\llbracket\neg A\rrbracket_v=1-\llbracket A\rrbracket_v,$$

$$\llbracket A\land B\rrbracket_v=1 \text{ iff both values are }1,$$

$$\llbracket A\lor B\rrbracket_v=1 \text{ iff at least one value is }1,$$

$$\llbracket A\to B\rrbracket_v=0 \text{ iff }\llbracket A\rrbracket_v=1\text{ and }\llbracket B\rrbracket_v=0,$$

$$\llbracket A\leftrightarrow B\rrbracket_v=1 \text{ iff }\llbracket A\rrbracket_v=\llbracket B\rrbracket_v.$$

The symbols $1$ and $0$ denote truth values, not object-language formulas.
