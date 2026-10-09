For compactness write $T(a,b,c)=\left(\begin{smallmatrix}a&b\\0&c\end{smallmatrix}\right)$. Direct multiplication gives

$$
T(a,b,c)T(a',b',c')=T(aa',ab'+bc',cc').
$$

Since $a,c\ne0$, inverses also exist in $G$:

$$
T(a,b,c)^{-1}=T(a^{-1},-a^{-1}bc^{-1},c^{-1}).
$$

These formulas also verify the subgroup assertion.

**(a) The first diagonal entry.** The product formula gives $\varphi(TT')=aa'=\varphi(T)\varphi(T')$. For any $t\in F^\times$, $T(t,0,1)$ maps to $t$, proving surjectivity. By definition a fiber consists of precisely those matrices with prescribed image. Therefore

$$
\varphi^{-1}(t)=\{T(t,b,c):b\in F,\ c\in F^\times\},
$$

and

$$
\ker\varphi=\varphi^{-1}(1)=\{T(1,b,c):b\in F,\ c\in F^\times\}.
$$

Do not impose $c=1$ here: $\varphi$ does not inspect the lower diagonal entry.

**(b) Both diagonal entries.** Multiplication in the codomain is coordinatewise, so $\psi(TT')=(aa',cc')=(a,c)(a',c')$. The matrix $T(t,0,w)$ realizes any $(t,w)\in F^\times\times F^\times$. Thus $\psi$ is surjective, and

$$
\psi^{-1}(t,w)=\{T(t,b,w):b\in F\},\qquad\ker\psi=\{T(1,b,1):b\in F\}=H.
$$


**(c) The additive field.** Define $\theta:(F,+)\to H$ by $\theta(b)=T(1,b,1)$. The multiplication formula reduces to $\theta(b)\theta(b')=T(1,b+b',1)=\theta(b+b')$. Every element of $H$ has this form, and equality of the upper-right entries shows that $\theta$ is injective. Hence $\theta$ is an isomorphism.

**Technique:** compute the matrix product first; then read off the image and solve the fiber equation without adding unintended restrictions.

**Foundations:** @cu:algebra:midterm-2:definitions:df:normal-quotient, @cu:algebra:midterm-2:theorems:th:commutator-criterion.
