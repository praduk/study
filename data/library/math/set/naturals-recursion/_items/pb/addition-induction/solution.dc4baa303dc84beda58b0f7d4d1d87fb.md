For the first claim, induct on $n$. At $n=0$, $0+0=0$. If $0+n=n$, then

$$
0+S(n)=S(0+n)=S(n).
$$

Thus $0+n=n$ for all $n$.

For associativity, fix $a$ and $b$ and induct on $c$. At $c=0$,

$$
(a+b)+0=a+b=a+(b+0).
$$

Assume $(a+b)+c=a+(b+c)$. Then

$$
\begin{aligned}
(a+b)+S(c)
&=S((a+b)+c)\\
&=S(a+(b+c))\\
&=a+S(b+c)\\
&=a+(b+S(c)).
\end{aligned}
$$

The first and last equalities use recursion in the second argument, and the middle equality uses the induction hypothesis. Therefore addition is associative.
