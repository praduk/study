Call a function $s$ a valid approximation if its domain is $S(n)=n\cup\{n\}$ for some $n\in\omega$, $s(0)=a$, and $s(S(k))=g(s(k))$ whenever $S(k)$ lies in its domain. Every such $s$ is a subset of $\omega\times A$, so the collection $C$ of valid approximations is a set by Separation from $\mathcal{P}(\omega\times A)$.

Induction on $n$ shows that there is exactly one valid approximation with domain $S(n)$. The base approximation is $\{\langle0,a\rangle\}$. Given the unique approximation through $n$, append
$\langle S(n),g(s(n))\rangle$; uniqueness at the next stage follows because the recursion rule forces the new value.

Two valid approximations agree on their common domain: apply induction up to the smaller domain. Therefore $f=\bigcup C$ is a function. Every $n\in\omega$ lies in $S(n)$, so $f$ has domain $\omega$; its range lies in $A$, and it satisfies the two recursion equations.

If $h$ is another such function, induction on $n$ gives $h(n)=f(n)$: it holds at $0$, and equality at $n$ implies
$h(S(n))=g(h(n))=g(f(n))=f(S(n))$. Hence $h=f$.
