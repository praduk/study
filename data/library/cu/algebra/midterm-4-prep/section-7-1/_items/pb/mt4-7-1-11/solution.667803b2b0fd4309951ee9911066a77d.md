**Strategy.** Factor $x^2-1$. In an @[integral domain]mt4-integral-domain, a product can be zero only if at least one factor is zero.

**Factor the equation.** By @[distributivity]mt4-ring and the @[ring sign rules]mt4-ring-arithmetic,

$$
(x-1)(x+1)=x^2+x-x-1=x^2-1=0.
$$

**Read off the possibilities.** If $x-1=0$, then $x=1$. If $x-1\ne0$, apply @[cancellation]mt4-cancellation to $(x-1)(x+1)=(x-1)0$ to get $x+1=0$, hence $x=-1$. These values coincide when $1=-1$ in $R$.
