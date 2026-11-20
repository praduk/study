Let $F$ be a @[field]mt4-field and define the ring $F((x))$ of *@[formal Laurent series]mt4-laurent-series* with coefficients from $F$ by

$$
F((x))=\left\{\sum_{n\ge N}^{\infty}a_nx^n\;\middle|\;a_n\in F\text{ and }N\in\Z\right\}.
$$

(Every element of $F((x))$ is a power series in $x$ plus a polynomial in $1/x$, i.e., each element of $F((x))$ has only a finite number of terms with negative powers of $x$.)

**(a)** Prove that $F((x))$ is a field.

**(b)** Define the map

$$
v:F((x))^{\times}\to\Z\qquad\text{by}\qquad v\Bigl(\sum_{n\ge N}^{\infty}a_nx^n\Bigr)=N
$$

where $a_N$ is the first nonzero coefficient of the series (i.e., $N$ is the “order of zero or pole of the series at $0$”). Prove that $v$ is a @[discrete valuation]mt4-discrete-valuation on $F((x))$ whose @[discrete valuation ring]mt4-discrete-valuation is $F[[x]]$, the ring of @[formal power series]mt4-power-series (cf. Exercise 26, Section 1).
