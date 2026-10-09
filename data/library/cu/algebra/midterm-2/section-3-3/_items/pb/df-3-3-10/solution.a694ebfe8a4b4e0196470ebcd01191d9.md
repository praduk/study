Put $h=|H|$, $d=[G:H]$, and $t=|H\cap N|$. Since $HN$ is a subgroup containing $H$, multiplicativity of indices gives

$$
[G:H]=[G:HN][HN:H].
$$

The product-order formula gives $[HN:H]=|N|/t=[N:H\cap N]$. Thus $[N:H\cap N]$ divides $d$. Also $t$ divides $h$. A common prime divisor of $t$ and $[N:H\cap N]$ would then divide both $h$ and $d$, contradicting the Hall condition. Hence $H\cap N$ is Hall in $N$.

Next, the second isomorphism theorem gives $|HN/N|=h/t$, which divides $h$. The index of that subgroup in $G/N$ is

$$
[G/N:HN/N]=[G:HN],
$$

which divides $d$ by the first displayed equality. Again a common prime divisor would divide both $h$ and $d$. Therefore $HN/N$ is Hall in $G/N$.

**Technique:** prove the two quantities whose gcd is needed divide the original coprime pair. This avoids assuming $H$ itself is normal.

**Foundations:** @cu:algebra:midterm-2:theorems:th:first-isomorphism, @cu:algebra:midterm-2:theorems:th:second-isomorphism, @cu:algebra:midterm-2:theorems:th:correspondence, @cu:algebra:midterm-2:theorems:th:product-order.
