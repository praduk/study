**Strategy.** Use @[the definition of a PID]mt4-pid as a checklist. First show that $R/P$ is a domain. Then take an arbitrary ideal in the quotient and find a single element that generates it.

**Show the quotient is a domain.** The ideal $P$ is prime, so the @[prime ideal quotient criterion]mt4-prime-quotient-domain gives that $R/P$ is an integral domain.

**Pass a generator to the quotient.** For any ideal $J$ of $R/P$, @[ideal correspondence]mt4-ideal-correspondence gives an ideal $I$ of $R$ containing $P$ with $J=I/P$. Since $R$ is a PID, choose $a$ with $I=(a)$. Every element of $J$ has the form $ra+P$, and @[quotient multiplication]mt4-quotient-operations gives $ra+P=(r+P)(a+P)$. Conversely $a+P\in J$, so all its multiples belong to $J$. Thus $J=(a+P)$, completing the PID checklist.

**Alternative using maximal ideals.** If $P=(0)$, then $r\mapsto r+(0)$ identifies the quotient with $R$. If $P\ne(0)$, the @[nonzero prime ideal theorem for PIDs]mt4-pid-prime-maximal makes $P$ maximal. The quotient is then a field by the @[maximal ideal quotient criterion]mt4-maximal-quotient-field. A field is an @[integral domain]gre:mathematics-subject-test:abstract-algebra:th:field-domain whose @[only ideals]mt4-field-ideal-test are $(0)$ and $(1)$, so it is a PID.
