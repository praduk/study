If $R$ is a @[PID]mt4-pid, every two-generated ideal is principal by definition, so $R$ is a @[Bézout domain]mt4-bezout-domain. It is a UFD by @[Theorem 14]mt4-pid-ufd.

Conversely, let $I\ne(0)$ be an ideal of a Bézout domain that is also a UFD. For $x\ne0$ let $\ell(x)$ be the number of irreducible factors counted with multiplicity, counting a unit as zero. By @[unique factorization]mt4-ufd, this is well defined, adds under multiplication, and is positive on every nonzero nonunit. Choose $a\in I\setminus\{0\}$ minimizing $\ell(a)$.

If some $b\in I$ lay outside $(a)$, then $(a,b)=(d)$ for some nonzero $d\in I$. Write $a=dt$. A unit $t$ would imply $(d)=(a)$ and hence $b\in(a)$. Therefore $t$ is a nonunit, giving $\ell(d)=\ell(a)-\ell(t)<\ell(a)$, a contradiction. Thus $I=(a)$. The zero ideal is already principal, proving the converse.
