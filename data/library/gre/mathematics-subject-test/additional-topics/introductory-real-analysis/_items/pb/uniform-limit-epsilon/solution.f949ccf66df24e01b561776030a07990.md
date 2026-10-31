**Answer.** Yes.

**Pattern cue.** Use a three-term error bound with one fixed approximating function.

**Fast route.** Given $\varepsilon>0$, choose $N$ with $2\cdot2^{-N}<\varepsilon/2$. At a fixed point $x_0$, continuity of $f_N$ makes $|f_N(x)-f_N(x_0)|<\varepsilon/2$ for nearby $x$. The two uniform errors plus this middle error give $|f(x)-f(x_0)|<\varepsilon$.

**Trap.** Choose $N$ once for the desired tolerance before using continuity; do not let it vary uncontrollably with $x$.

**Recall.** @gre:mathematics-subject-test:additional-topics:introductory-real-analysis:th:uniform-limit-continuity.
