**Strategy.** Test the two operations separately. Linearity handles addition. To disprove multiplicativity, it suffices to find one continuous function whose square has the wrong integral.

**Verify the additive homomorphism.** Every continuous function on $[0,1]$ is @[Riemann integrable]math:uganalysis:riemann-integration:th:continuous-integrability, so $\varphi$ is defined on all of $R$. By @[linearity of the integral]math:uganalysis:riemann-integration:th:integral-algebra,

$$
\varphi(f+g)=\int_0^1(f(t)+g(t))\,dt=\varphi(f)+\varphi(g).
$$

This is the @[group homomorphism condition]cu:algebra:wk1:df:mt-homomorphism for the additive groups.

**Exhibit the failure of multiplication.** In the @[pointwise function ring]mt4-function-ring take $f(t)=t$, so $f^2(t)=t^2$. The @[power antiderivatives]gre:mathematics-subject-test:single-variable-calculus:th:power-antiderivative and the @[fundamental theorem of calculus]math:uganalysis:riemann-integration:th:fundamental-theorem give

$$
\varphi(f^2)=\int_0^1 t^2\,dt=\tfrac13,
\qquad
\varphi(f)^2=\left(\int_0^1 t\,dt\right)^2=\tfrac14.
$$

A @[ring homomorphism]mt4-ring-homomorphism must preserve every product, in particular $f\cdot f$. The unequal values disprove that property.
