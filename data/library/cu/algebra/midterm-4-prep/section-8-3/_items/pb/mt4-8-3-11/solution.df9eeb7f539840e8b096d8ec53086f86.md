**Strategy.** The forward direction follows from the standard properties of a PID. For the converse, take an arbitrary nonzero ideal and choose an element with the fewest irreducible factors. Use the Bézout property to show that adjoining any element outside its principal ideal would produce an even shorter factorization.

**From a PID to both properties.** In a @[PID]mt4-pid all ideals are principal, so every two-generated ideal is principal. This is the @[Bézout property]mt4-bezout-domain. The @[PID factorization theorem]mt4-pid-ufd also gives that $R$ is a UFD.

**From a UFD with the Bézout property to a PID.** Fix an ideal $I\ne(0)$. For nonzero $x$, let $\ell(x)$ be its number of irreducible factors counted with multiplicity, taking $\ell(x)=0$ for a unit. By @[unique factorization]mt4-ufd this count is well defined. Multiplying two nonzero elements concatenates their factors, so their counts add. By the @[well-ordering of the nonnegative integers]math:set:orders-well-orders:df:well-order, choose $a\in I\setminus\{0\}$ with the least possible count.

**Show that $a$ generates $I$.** Suppose there were $b\in I$ outside $(a)$. By the Bézout property, $(a,b)=(d)$ for some $d$. Since $a\ne0$ and $(a,b)\subseteq I$, we have $d\ne0$ and $d\in I$. Write $a=dt$.

If $t$ were a unit, then $a$ and $d$ would be @[associates]mt4-associates. This would give $b\in(d)=(a)$, a contradiction. Thus $t$ is a nonzero nonunit and $\ell(t)\ge1$. It follows that $\ell(d)=\ell(a)-\ell(t)<\ell(a)$, contradicting the minimal choice of $a$ in $I$.

Therefore every $b\in I$ belongs to $(a)$. The reverse inclusion follows from $a\in I$, so $I=(a)$. The remaining ideal $(0)$ is already principal. Hence $R$ is a PID.
