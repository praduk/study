Use the @[annihilator definitions]mt4-annihilator and the @[ideal tests]mt4-ideal.

**(a)** Both sets contain zero by the @[zero product identities]mt4-ring-arithmetic. Use @[distributivity and associativity]mt4-ring to check closure. If $ax=ay=0$, then $a(x-y)=0$, and $a(xr)=(ax)r=0$ for every $r$. This proves the right ideal claim. If $xa=ya=0$, then $(x-y)a=0$, and $(rx)a=r(xa)=0$, giving the left ideal claim.

**(b)** Write $A$ for the left annihilator of $L$. It contains zero, and for $x,y\in A$ and $a\in L$, $(x-y)a=xa-ya=0$. For $x\in A$ and $r\in R$, both products annihilate $L$ on the left. Indeed, $(rx)a=r(xa)=0$, while $(xr)a=x(ra)=0$ because $ra\in L$. This last step is where the left ideal hypothesis is used.
