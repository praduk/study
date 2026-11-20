**Strategy.** Count the possible remainders of degree less than $n$, including the zero polynomial. To count classes this way, first check that each class is counted exactly once.

**1. Match each class to a coefficient tuple.** Send $(c_0,\ldots,c_{n-1})\in F^n$ to the class of $c_0+c_1x+\cdots+c_{n-1}x^{n-1}$. By @[polynomial division]mt4-division-polynomials every class occurs. By @[uniqueness of the remainder in Exercise 1]mt4-9-2-1, two tuples give the same class only if all their coefficients agree. This is a @[bijection]math:set:cardinality-countability:df:equinumerosity.

**2. Count the tuples.** Each of the $n$ positions has $q$ independent choices, including zero. The @[multiplication principle]gre:mathematics-subject-test:discrete-mathematics:th:multiplication-counting gives $|F[x]/(f)|=|F^n|=q^n$. This count also applies when $f$ is reducible.
