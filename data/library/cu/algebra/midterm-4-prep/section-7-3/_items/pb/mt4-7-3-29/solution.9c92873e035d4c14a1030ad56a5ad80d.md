**Strategy.** Apply the @[ideal test]mt4-ideal to the set of nilpotent elements. For subtraction, find a power of $a-b$ large enough that every term contains either a vanishing power of $a$ or a vanishing power of $b$.

**1. Verify that zero belongs.** Write $N=\mathfrak N(R)$ for the @[nilradical]mt4-nilradical, the set of nilpotent elements. Since $0^1=0$, we have $0\in N$.

**2. Prove closure under subtraction.** For $a,b\in N$, @[nilpotence]mt4-nilpotent gives positive integers $m,n$ with $a^m=b^n=0$. Expand $(a-b)^{m+n-1}$ by distributivity. Each product in the expansion uses $m+n-1$ factors, each equal to $a$ or $-b$.

- If the product contains at least $m$ copies of $a$, commutativity lets us group $m$ of them into the factor $a^m=0$.
- Otherwise it contains at most $m-1$ copies of $a$, leaving at least $(m+n-1)-(m-1)=n$ copies of $-b$. These give the factor $(-b)^n=0$.

Every product is zero, so $(a-b)^{m+n-1}=0$ and $a-b\in N$. The same count with $b$ in place of $-b$ gives $(a+b)^{m+n-1}=0$, which proves the addition claim in the hint. This is the counting argument behind the @[binomial expansion]mt4-binomial-theorem. Working directly with products of positive length also covers rings without an identity.

**3. Prove absorption by the ring.** For $a\in N$ and $r\in R$, commutativity gives $(ra)^m=r^m a^m=0$, just as in @[Exercise 7.1.14(b)]mt4-7-1-14. Hence $ra=ar\in N$. The three checks prove that $N$ is an ideal.
