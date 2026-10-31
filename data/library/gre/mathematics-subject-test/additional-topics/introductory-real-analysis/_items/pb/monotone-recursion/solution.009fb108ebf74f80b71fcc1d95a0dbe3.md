**Answer.** $2$.

**Pattern cue.** Prove a bound and monotonicity before taking limits.

**Fast route.** Inductively $1\le a_n<2$. For $1\le x<2$, $2+x>x^2$ because $(2-x)(x+1)>0$, so $a_{n+1}>a_n$. Thus a limit $L\in[1,2]$ exists, and continuity gives $L^2=2+L$, whose eligible root is two.

**Trap.** Solving the fixed-point equation alone does not prove convergence.

**Recall.** @gre:mathematics-subject-test:additional-topics:introductory-real-analysis:th:monotone-sequences.
