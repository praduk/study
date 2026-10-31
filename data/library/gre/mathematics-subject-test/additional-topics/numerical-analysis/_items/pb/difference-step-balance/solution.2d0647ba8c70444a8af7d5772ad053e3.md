**Answer.** $h=(\varepsilon/2)^{1/3}$.

**Pattern cue.** Balance decreasing truncation error against increasing roundoff.

**Fast route.** $E'(h)=2h-\varepsilon/h^2=0$ gives $2h^3=\varepsilon$. Since $E''(h)=2+2\varepsilon/h^3>0$ and the bound tends to infinity at both ends, this is the unique minimum.

**Trap.** The optimum of this model is not a universal finite-difference step size.

**Recall.** @gre:mathematics-subject-test:additional-topics:numerical-analysis:rk:cancellation; @gre:mathematics-subject-test:additional-topics:numerical-analysis:rk:finite-differences.
