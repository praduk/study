**Answer.** $x=(1,1)^T$, error $1$, residual $10^{-6}$.

**Pattern cue.** A small matrix scale can hide a large solution error.

**Fast route.** $Ax=b$ gives $x_1=x_2=1$. The error vector is $(0,-1)$, while $A\widehat x-b=(0,-10^{-6})$.

**Trap.** Residual size alone is not a forward-error certificate.

**Recall.** @gre:mathematics-subject-test:additional-topics:numerical-analysis:df:forward-backward-error.
