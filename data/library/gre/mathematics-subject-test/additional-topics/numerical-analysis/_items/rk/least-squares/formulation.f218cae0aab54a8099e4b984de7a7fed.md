Interpolation fits every data point exactly, whereas least squares minimizes the sum of squared residuals and need not pass through any point. For a full-column-rank matrix $A$, the least-squares solution satisfies $A^TAx=A^Tb$ over $\R$. In the Euclidean norm, $\kappa_2(A^TA)=\kappa_2(A)^2$; solving via QR avoids this squaring in the formed system.

**Pattern practice.** @gre:mathematics-subject-test:additional-topics:numerical-analysis:pb:constant-least-squares; @gre:mathematics-subject-test:additional-topics:numerical-analysis:pb:normal-equation-condition.
