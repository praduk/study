**Answer.** $2x+h$, with signed error $h$.

**Pattern cue.** Expand one shifted value rather than a symmetric pair.

**Fast route.** $(x+h)^2-x^2=2xh+h^2$, so division gives $2x+h$. Subtract the exact derivative $2x$.

**Trap.** A forward difference generally has a first-order error term even where the centered difference is exact.

**Recall.** @gre:mathematics-subject-test:additional-topics:numerical-analysis:rk:finite-differences.
