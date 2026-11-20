**Strategy.** Use the @[ideal tests]mt4-ideal. Each @[annihilator]mt4-annihilator must contain zero and be closed under subtraction. Then test multiplication on the indicated side in (a) and on both sides in (b), keeping the order of factors fixed.

**(a) The right annihilator is a right ideal.** Write $A_r=\{x\in R:ax=0\}$. It contains zero since @[multiplication by zero]mt4-ring-arithmetic gives $a0=0$. If $x,y\in A_r$ and $r\in R$, @[distributivity and associativity]mt4-ring give

$$
a(x-y)=ax-ay=0,\qquad a(xr)=(ax)r=0.
$$

Thus $x-y$ and $xr$ lie in $A_r$, as required.

**(a) The left annihilator is a left ideal.** Write $A_\ell=\{x\in R:xa=0\}$. Again $0\in A_\ell$. For $x,y\in A_\ell$ and $r\in R$,

$$
(x-y)a=xa-ya=0,\qquad (rx)a=r(xa)=0.
$$

Here the elements that remain in $A_\ell$ are $x-y$ and $rx$.

**(b) The left annihilator of a left ideal is two-sided.** Let $A=\{x\in R:xa=0\text{ for all }a\in L\}$. It contains zero, and for $x,y\in A$ and every $a\in L$, $(x-y)a=xa-ya=0$. Thus $x-y\in A$.

To check both sides, take $x\in A$, $r\in R$, and any $a\in L$.

- **Left multiplication.** $(rx)a=r(xa)=0$, so $rx\in A$.
- **Right multiplication.** Since $L$ is a left ideal, $ra\in L$. Therefore $(xr)a=x(ra)=0$, so $xr\in A$.

This proves two-sided absorption. The right multiplication check is precisely where the left ideal property of $L$ enters.
