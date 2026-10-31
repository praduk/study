**Answer.** $A(x)=1/[(1-x)(1-2x)]$.

**Pattern cue.** Account for the missing constant term when shifting a recurrence.

**Fast route.** Summing for $n\ge1$ gives $A-1=2xA+x/(1-x)$. Thus $(1-2x)A=1/(1-x)$. Independently, $a_n=2^{n+1}-1$ has the same generating function.

**Trap.** Writing $A=2xA+\cdots$ would omit $a_0$.

**Recall.** @gre:mathematics-subject-test:additional-topics:combinatorics:rk:generating-functions; @gre:mathematics-subject-test:additional-topics:combinatorics:rk:recurrence-roots.
