Every continuous function on $[0,1]$ is @[Riemann integrable]math:uganalysis:riemann-integration:th:continuous-integrability, so $\varphi$ is defined on all of $R$. By @[linearity of the integral]math:uganalysis:riemann-integration:th:integral-algebra, $\varphi(f+g)=\varphi(f)+\varphi(g)$. This is the @[group homomorphism condition]cu:algebra:wk1:df:mt-homomorphism for the additive groups.

To test multiplication in the @[pointwise function ring]mt4-function-ring, take $f(t)=t$. The @[power antiderivatives]gre:mathematics-subject-test:single-variable-calculus:th:power-antiderivative and the @[fundamental theorem of calculus]math:uganalysis:riemann-integration:th:fundamental-theorem give

$$
\varphi(f^2)=\int_0^1 t^2\,dt=\tfrac13,\qquad
\varphi(f)^2=\left(\int_0^1 t\,dt\right)^2=\tfrac14.
$$

Since the two values differ, the product condition in the @[definition of a ring homomorphism]mt4-ring-homomorphism fails.
