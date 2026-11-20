Set $K=\ker\varphi$. By the @[kernel and image properties]mt4-kernel-image, $K$ is a two-sided ideal and $\im\varphi$ is a subring of $S$. Define $\bar\varphi:R/K\to\im\varphi$ by $\bar\varphi(a+K)=\varphi(a)$.

By @[equality of quotient classes]mt4-quotient-ring, $a+K=b+K$ exactly when $a-b\in K$. By @[additivity and the kernel definition]mt4-ring-homomorphism, this last condition says $\varphi(a)-\varphi(b)=0$. In one direction this proves that $\bar\varphi$ is well-defined; in the other it proves injectivity.

Every element of $\im\varphi$ has the form $\varphi(a)$, so $\bar\varphi$ is onto. It preserves sums because $\varphi(a+b)=\varphi(a)+\varphi(b)$ and products because $\varphi(ab)=\varphi(a)\varphi(b)$. Thus it is a @[ring isomorphism]mt4-ring-isomorphism.
