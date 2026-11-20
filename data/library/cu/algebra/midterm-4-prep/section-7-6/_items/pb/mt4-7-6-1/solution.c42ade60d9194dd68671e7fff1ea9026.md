**Strategy.** Split $1$ as $e+(1-e)$. Show that the two summands are central idempotents that multiply to zero. Multiplication by them will split each $r\in R$ into two coordinates that can be recovered by addition.

**1. Compute the products of the two summands.** Put $h=1-e$. Since $e$ is a @[central idempotent]mt4-central-idempotent, $h$ also commutes with every element of $R$. Moreover,

$$
h^2=1-2e+e^2=h,\qquad eh=he=e-e^2=0.
$$

**2. Check the two ideals and their identities.** Take $c=e$ or $c=h$. The set $Rc$ contains $0$ and is closed under differences since $rc-sc=(r-s)c$. For $t\in R$, left multiplication gives $t(rc)=(tr)c$, and centrality gives $(rc)t=(rt)c$. Thus $Rc$ is a @[two-sided ideal]mt4-ideal and hence a @[subring]mt4-subring. Since $c^2=c$ and $c$ is central, $c(rc)=(rc)c=rc$. This gives identity $e$ in $Re$ and identity $h$ in $Rh$, including the zero-ring factor when $c=0$.

**3. Construct the isomorphism.** Define $\phi:R\to Re\times Rh$ by $\phi(r)=(re,rh)$. Addition is preserved by distributivity. Under the @[direct product operations]mt4-direct-product-rings, multiplication is preserved in each coordinate since $(rc)(sc)=rsc^2=rsc$. Also, $\phi(1)=(e,h)$.

**4. Recover the original element.** The inverse sends $(u,v)$ to $u+v$. Indeed, if $u\in Re$ and $v\in Rh$, then $ue=u$, $vh=v$ and $uh=ve=0$. Thus $\phi(u+v)=(u,v)$. Conversely, adding the coordinates of $\phi(r)$ returns $re+rh=r(e+h)=r$. Hence $\phi$ is a @[ring isomorphism]mt4-ring-isomorphism.
