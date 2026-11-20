**Strategy.** Run the Euclidean algorithm forward to find the monic gcd. Then read the remainder equations backward to express the gcd as $Aa+Bb$.

**1. Find the last nonzero remainder.** Use @[polynomial division]mt4-division-polynomials and set $q=x^2-4x+15$, $c=10x^2+9x-19$. With denominators cleared, the successive divisions give

$$
\begin{aligned}
b&=qa-5c,\\
100a&=(10x+31)c+11(x-1),\\
c&=(10x+19)(x-1).
\end{aligned}
$$

The last line has zero remainder. The preceding remainder is a nonzero rational multiple of $x-1$. Since nonzero rational constants are @[units]mt4-polynomial-domains, the rescalings preserve divisibility. By the @[Euclidean algorithm]mt4-euclidean-gcd, the @[monic]mt4-polynomial-ring gcd is $x-1$.

**2. Recover the Bézout coefficients.** Solve the first line for $5c=qa-b$. Multiply the second line by $5$ and substitute to obtain

$$
55(x-1)=500a-(10x+31)(qa-b).
$$

Collect the coefficients of $a$ and $b$, expand $q$, and divide by $55$. This gives $Aa+Bb=x-1$ with

$$
\begin{aligned}
A&=\frac{-10x^3+9x^2-26x+35}{55},\\
B&=\frac{10x+31}{55}.
\end{aligned}
$$

**3. Verify the gcd in both directions.** Since $a(1)=b(1)=0$, the @[factor theorem]gre:mathematics-subject-test:abstract-algebra:th:remainder-factor shows $x-1$ divides both polynomials. Conversely, every common divisor of $a$ and $b$ divides $Aa+Bb=x-1$. These are exactly the two requirements in the @[definition of a gcd]mt4-divisibility-gcd.
