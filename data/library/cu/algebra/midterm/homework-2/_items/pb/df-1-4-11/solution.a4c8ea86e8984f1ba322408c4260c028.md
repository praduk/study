(a) Direct multiplication gives

$$
X(a,b,c)X(d,e,f)=X(a+d,b+e+af,c+f).
$$

Thus the product is in $H(F)$. For $X=X(1,0,0)$ and $Y=X(0,0,1)$, $XY=X(1,1,1)$ but $YX=X(1,0,1)$, over every field.

(b) Solving the product formula for the identity gives

$$
X(a,b,c)^{-1}=X(-a,ac-b,-c).
$$

Substitution in both product orders yields $X(0,0,0)=I$.

(e) By induction, for positive integers $m$,

$$
X(a,b,c)^m=X\left(ma,\ mb+\binom m2 ac,\ mc\right).
$$

Indeed the next multiplication adds $a,c$ to the outer coordinates and adds $b+mac$ to the middle coordinate. If this power equals $I$ over $\R$, then $ma=mc=0$ forces $a=c=0$, and then $mb=0$ forces $b=0$. Therefore no nonidentity element has a positive identity power.

**Technique:** encode a matrix by its free coordinates; use induction on powers. The conclusion in (e) depends on characteristic zero and fails over finite fields.
