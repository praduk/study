Call $f$ an approximation through $\alpha$ if $\operatorname{dom}(f)=\alpha+1$ and
$\varphi(f\mathbin{\upharpoonright}\beta,f(\beta),\vec p)$ holds for every $\beta\le\alpha$.

Two approximations agree on their common domain. Otherwise their least point of disagreement $\gamma$ would have identical restrictions below $\gamma$. Both values at $\gamma$ satisfy $\varphi$ for that same restriction, so the assumed uniqueness would force them to be equal.

We prove by transfinite induction that an approximation through every $\alpha<\theta$ exists. Assume approximations exist through all $\beta<\alpha$. They are unique by the preceding paragraph, and “$f$ is the approximation through $\beta$” is first-order definable from $\varphi$ and $\vec p$. Replacement therefore collects them into a set. Their union $h$ is a function with domain $\alpha$ because they are compatible. Let $y$ be the unique set with $\varphi(h,y,\vec p)$, and append $\langle\alpha,y\rangle$. The resulting function is an approximation through $\alpha$. This also handles $0$ and limit stages: at $0$ the prior union is empty, while at a limit it glues all earlier approximations.

Replacement now collects the unique approximation through each $\alpha<\theta$; their union is a function $F$ on $\theta$, and the construction gives the required instances of $\varphi$. If $F'$ also satisfies them, a least point at which $F$ and $F'$ differ yields the same uniqueness contradiction used for approximations. Hence $F$ is unique.
