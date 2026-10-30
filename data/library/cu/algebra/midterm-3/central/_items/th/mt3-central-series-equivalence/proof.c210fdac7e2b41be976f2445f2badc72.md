**Definitions and result used:** @mt3-upper-central, @mt3-lower-central, @mt3-series-functorial.

Put $Z=Z(G)$. The upper-series definition gives

$$
Z_i(G/Z)=Z_{i+1}(G)/Z\qquad(i\ge0),
$$

by induction: quotienting the next center on either side gives the same quotient $G/Z_{i+1}(G)$. Also surjective functoriality gives $L_i(G/Z)=L_i(G)Z/Z$.

Induct on $c$. For $c=0$, both assertions say $G=1$. If $Z_c(G)=G$, the upper-series identity and induction imply $L_{c-1}(G/Z)=1$. Hence $L_{c-1}(G)\le Z$, and $L_c(G)=[G,L_{c-1}(G)]=1$.

Conversely, if $L_c(G)=1$, then every element of $L_{c-1}(G)$ commutes with $G$, so $L_{c-1}(G)\le Z$. The quotient has lower term $c-1$ equal to $1$. Induction and the upper-series identity imply $Z_c(G)=G$.
