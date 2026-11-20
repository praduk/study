Put $h=1-e$. Since $e$ is a @[central idempotent]mt4-central-idempotent, $h$ commutes with every $r\in R$. Also $h^2=1-2e+e^2=h$ and $eh=he=e-e^2=0$.

For $c=e$ or $c=h$, the set $Rc$ contains zero and is closed under differences since $rc-sc=(r-s)c$. It absorbs multiplication on the left and right since $t(rc)=(tr)c$ and $(rc)t=(rt)c$ by centrality. Thus it is a @[two-sided ideal]mt4-ideal and hence a @[subring]mt4-subring. The equality $c(rc)=(rc)c=rc$ makes $c$ its identity. This includes $c=0$, where the factor is the zero ring.

Define $\phi:R\to Re\times Rh$ by $\phi(r)=(re,rh)$. With the @[direct product operations]mt4-direct-product-rings it is additive, and $(rc)(sc)=rsc^2=rsc$ gives multiplicativity in each coordinate. Its inverse is $(u,v)\mapsto u+v$. Indeed, for $u\in Re$, $v\in Rh$, the identities $ue=u$, $vh=v$ and $uh=ve=0$ give $\phi(u+v)=(u,v)$. Conversely $re+rh=r$. Hence $\phi$ is a @[ring isomorphism]mt4-ring-isomorphism, and it takes $1_R$ to $(e,h)$.
