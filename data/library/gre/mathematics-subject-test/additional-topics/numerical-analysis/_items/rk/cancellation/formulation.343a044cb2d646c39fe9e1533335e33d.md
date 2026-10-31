Subtracting nearly equal floating-point values may lose relative accuracy because the difference is small compared with errors in its operands. Algebraic reformulation can avoid it; for $x>0$, $\sqrt{x+1}-\sqrt x=1/(\sqrt{x+1}+\sqrt x)$. The exact formulas agree, but their numerical behavior need not. Smaller steps are not always better when roundoff is amplified.

**Pattern practice.** @gre:mathematics-subject-test:additional-topics:numerical-analysis:pb:radical-difference; @gre:mathematics-subject-test:additional-topics:numerical-analysis:pb:difference-step-balance.
