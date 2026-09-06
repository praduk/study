Fix an arbitrary valuation and abbreviate the truth values of $A,B,C$ by $a,b,c\in\{0,1\}$. Double negation applies $a\mapsto1-a$ twice. Each De Morgan pair has the same truth condition: $\neg(A\land B)$ is true exactly when not both $a,b$ are $1$, exactly when $a=0$ or $b=0$; the dual says not at least one is $1$, exactly when both are $0$.

An implication is false exactly in the case $a=1,b=0$, which is also the only case in which $\neg A\lor B$ is false. A biconditional is true exactly when $a=b$; this is exactly when both directed implications are true.

Commutativity follows because 'both' and 'at least one' are symmetric. Associativity follows because either bracketing of three conjunctions is true exactly when $a=b=c=1$, and either bracketing of three disjunctions is true exactly when at least one of $a,b,c$ is $1$. For distributivity, $a=1$ and either $b=1$ or $c=1$ holds exactly when either $a=b=1$ or $a=c=1$; the dual argument interchanges 'both' and 'at least one'.

The identity and domination laws follow immediately by fixing the constant input at $1$ or $0$. Finally, exactly one of $a$ and $1-a$ is $1$, so excluded middle always has value $1$ and a contradiction always has value $0$. Since the valuation was arbitrary, every displayed pair is logically equivalent.
