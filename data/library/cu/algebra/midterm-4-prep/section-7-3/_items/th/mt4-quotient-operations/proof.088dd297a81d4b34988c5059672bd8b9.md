Every subgroup of the abelian additive group of $R$ is normal: $r+i-r=i$ for $i\in I$. Thus the @[quotient group construction]math:algebra:groups-actions:df:normal-quotient already gives the additive group of cosets.

Suppose $I$ is a @[two-sided ideal]mt4-ideal. Replace $r,s$ by $r+i,s+j$ with $i,j\in I$. By @[distributivity]mt4-ring,

$$
(r+i)(s+j)-rs=rj+is+ij\in I.
$$

Thus both products represent the same coset. To check associativity and distributivity, take representatives and apply the corresponding identities in $R$. For instance $((r+I)(s+I))(t+I)=(rs)t+I=r(st)+I$.

Conversely, suppose multiplication on cosets is independent of representatives. For $i\in I$, the cosets $i+I$ and $0+I$ agree. Multiplying by $r+I$ on either side and using the @[zero product identities]mt4-ring-arithmetic gives $ri+I=I$ and $ir+I=I$. Thus $ri,ir\in I$. Together with the assumed additive subgroup property, this proves that $I$ is a two-sided ideal.
