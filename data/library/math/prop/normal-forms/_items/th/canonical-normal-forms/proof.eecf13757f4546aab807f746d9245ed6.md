Fix a total valuation $v$ and let $b=v|_P$ be its finite restriction. For every assignment $a:P\to\{0,1\}$, the minterm property gives $v\models m_a$ exactly when $b=a$. Hence $v$ satisfies the displayed DNF exactly when $m_b$ occurs in it, which is exactly when $b(A)=1$. By the finite-assignment evaluation definition, $b(A)=\llbracket A\rrbracket_v$, so the DNF and $A$ have the same value under $v$.

Dually, $v$ falsifies $k_a$ exactly when $b=a$. The displayed CNF is therefore false under $v$ exactly when its own maxterm $k_b$ occurs, which is exactly when $b(A)=0$, hence when $\llbracket A\rrbracket_v=0$. Thus the CNF and $A$ also agree under $v$. Since $v$ was an arbitrary total valuation, both normal forms are logically equivalent to $A$.

If no finite assignment makes $A$ true, the DNF is the empty disjunction $\false$. If no finite assignment makes $A$ false, the CNF is the empty conjunction $\true$. The same argument includes these boundary cases, including $P=\varnothing$.
