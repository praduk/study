**Strategy.** Write $G=\Z[i]$. For $(1+i)$, construct a map to $\F_2$ and identify its kernel. For a rational prime, use its Gaussian factorization to determine whether the quotient is a field or a product of fields. Count classes by reducing the real and imaginary coefficients separately.

**(a) Identify the quotient by $(1+i)$.** Send $a+bi$ to $a+b\bmod 2$. Substituting $1$ for $i$ respects $i^2=-1$ because $1=-1$ in $\F_2$, so this is a @[ring homomorphism]mt4-ring-homomorphism. Both $0$ and $1$ occur, making it surjective.

The kernel consists of Gaussian integers whose two coefficients have the same parity. This is exactly the condition that the quotient

$$
\frac{a+bi}{1+i}=\frac{a+b}{2}+\frac{b-a}{2}i
$$

has integer coefficients. Thus the kernel is $(1+i)$. The @[first isomorphism theorem]mt4-first-isomorphism gives $G/(1+i)\cong\F_2$, a field of order $2$.

**(b) Show $G/(q)$ is a field.** A prime $q\equiv3\pmod4$ remains irreducible in $G$ by the @[Gaussian prime classification]mt4-gaussian-primes. The ring $G$ is Euclidean by @[Gaussian division]mt4-gaussian-division and hence a PID by the @[Euclidean principal ideal theorem]mt4-euclidean-principal. In a PID an @[irreducible generates a maximal ideal]mt4-pid-prime-irreducible, so $(q)$ is maximal and its quotient is a field by the @[maximal ideal quotient criterion]mt4-maximal-quotient-field.

**Count its elements.** Two @[quotient classes]mt4-quotient-ring agree exactly when their difference is in $(q)$. Since $q$ is a rational integer, this means that the real coefficients agree modulo $q$ and the imaginary coefficients agree modulo $q$. There are $q$ independent choices for each, giving $q^2$ elements by the @[multiplication principle]gre:mathematics-subject-test:discrete-mathematics:th:multiplication-counting.

**(c) Check comaximality and apply the Chinese remainder theorem.** When $p\equiv1\pmod4$, the @[Gaussian prime classification]mt4-gaussian-primes gives $p=\pi\bar\pi$ with nonassociate irreducible factors. The ideals $(\pi)$ and $(\bar\pi)$ are distinct by the @[criterion for associates]mt4-associates and maximal by the PID argument in (b). Neither can contain the other. Their @[sum]mt4-ideal-sum-product therefore strictly contains $(\pi)$ and must equal $G$ by @[maximality]mt4-maximal-ideal.

The two ideals are thus @[comaximal]mt4-comaximal. The @[Chinese remainder theorem]mt4-chinese-remainder identifies their intersection with their product $(\pi\bar\pi)=(p)$. Reduction modulo the two factors gives the ring isomorphism

$$
G/(p)\cong G/(\pi)\times G/(\bar\pi).
$$

**Find the field orders.** Both factors are fields by maximality. The coefficient count from (b), now modulo $p$, gives $|G/(p)|=p^2$. Conjugation sends $(\pi)$ onto $(\bar\pi)$ and induces an isomorphism $z+(\pi)\mapsto\bar z+(\bar\pi)$, with conjugation again giving its inverse. Thus the factors have a common size $h$. Their @[direct product]mt4-direct-product-rings has $h^2=p^2$ elements, so each field has order $p$.
