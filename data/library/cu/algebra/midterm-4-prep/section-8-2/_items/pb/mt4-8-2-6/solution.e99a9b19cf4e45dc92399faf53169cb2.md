**Strategy.** Argue by contradiction. Choose a nonprincipal ideal $I$ maximal among such ideals. Every ideal strictly larger than $I$ must be principal. Use the failure of primality to build two larger ideals whose product turns out to be $I$ itself.

**(a) Use Zorn’s lemma to choose $I$.** Order the nonprincipal ideals by inclusion. For a nonempty chain, let $U$ be its union. It satisfies the @[ideal test]mt4-ideal. It contains $0$, two elements lie together in one chain member and have their difference there, and a ring multiple stays in the member containing its factor.

If $U=(u)$, then $u$ belongs to some chain member $K$. This forces $(u)\subseteq K\subseteq U=(u)$, making $K$ principal, a contradiction. Thus $U$ is a nonprincipal upper bound. The empty chain also has an upper bound because we assumed at least one nonprincipal ideal exists. Now @[Zorn’s lemma]mt4-zorn-lemma gives a maximal nonprincipal ideal $I$.

The whole ring is $(1)$, so $I$ is proper. By hypothesis every prime ideal is principal, so $I$ fails the @[prime ideal condition]mt4-prime-ideal. Choose $a,b\notin I$ with $ab\in I$.

**(b) Show $I_a$ and $J$ are principal.** The @[ideal sum]mt4-ideal-sum-product $I_a=I+(a)$ strictly contains $I$ because $a\notin I$. Thus $I_a=(\alpha)$ for some $\alpha$.

To use maximality again, check that $J=\{r\in R:rI_a\subseteq I\}$ is an ideal strictly larger than $I$.

- **Ideal test.** Zero lies in $J$. For $r,s\in J$ and $y\in I_a$, $(r-s)y=ry-sy\in I$. For $t\in R$, $(tr)y=t(ry)\in I$.
- **Strict containment.** Every $r\in I$ sends $I_a$ into $I$ by multiplication. Also $b(I+(a))\subseteq I$ because $bI\subseteq I$ and $ba\in I$. Hence $I\subsetneq I_b=I+(b)\subseteq J$, where strictness follows from $b\notin I$. Thus $J=(\beta)$ for some $\beta$.

**Show $I_aJ=(\alpha\beta)\subseteq I$.** By the @[definition of an ideal product]mt4-ideal-sum-product, the product consists of sums of products from the two ideals. All these products are multiples of $\alpha\beta$, and $\alpha\beta$ itself is in the product. Each product lies in $I$ by the defining property of $J$, giving the claimed inclusion.

**(c) Prove the reverse inclusion.** Given $x\in I$, we have $x\in I_a=(\alpha)$, say $x=s\alpha$. The coefficient $s$ belongs to $J$ because $sI_a=(s\alpha)=(x)\subseteq I$. Thus $x$ is a product of an element of $J$ and an element of $I_a$.

We have proved $I=I_aJ=(\alpha\beta)$, contradicting the choice of $I$. Therefore every ideal of the given domain is principal, so $R$ is a @[PID]mt4-pid.
