The probability is $q=(1+e^{\beta\Delta})^{-1}$. The energy variance is $\Delta^2q(1-q)$, so @physics:statistical:geometry:th:fisher-covariance gives

$$
G_{\beta\beta}=\Delta^2q(1-q),\qquad
G_{TT}=G_{\beta\beta}\left(\frac{d\beta}{dT}\right)^2
=\frac{\Delta^2q(1-q)}{k_B^2T^4}.
$$

Since $C_V=\Delta^2q(1-q)/(k_BT^2)$ by @physics:statistical:canonical:th:partition-derivatives, $G_{TT}=C_V/(k_BT^2)$. Therefore

$$
D(p_T\Vert p_{T+dT})=\frac{C_V}{2k_BT^2}(dT)^2+O(|dT|^3).
$$

The leading expression is dimensionless: $C_V/k_B$ is dimensionless and $(dT/T)^2$ is dimensionless. For every finite $T>0$, both state probabilities lie strictly between zero and one, so the one-dimensional metric is positive. A limiting endpoint such as $T=0$ is outside this parameter chart.
