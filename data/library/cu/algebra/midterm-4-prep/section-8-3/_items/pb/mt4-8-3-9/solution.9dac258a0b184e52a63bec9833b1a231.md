By @[the quadratic norm formula]mt4-quadratic-integers-norm and @[the unit criterion]mt4-quadratic-norm-units, $H(0)=0$, $H$ takes positive integer values on nonzero elements, is multiplicative, and $H(t)=1$ exactly for units. Take $\alpha,\beta\ne0$ with $\beta\nmid\alpha$. In a @[PID]mt4-pid write $(\alpha,\beta)=(\gamma)$, with $\gamma\ne0$. By @[Bézout’s identity]mt4-pid-bezout, this generator is a linear combination of the two inputs. Write $\beta=t\gamma$. If $t$ were a unit, $\beta$ and $\gamma$ would be @[associates]mt4-associates and $(\beta)=(\gamma)$ would contain $\alpha$, contradicting $\beta\nmid\alpha$. Since $t\ne0$ is a nonunit, $H(t)$ is an integer at least $2$. Therefore

$$
0<H(\gamma)<H(t)H(\gamma)=H(\beta).
$$

The element $\gamma\in(\alpha,\beta)$ meets the defining condition for @[a Dedekind–Hasse norm]mt4-dedekind-hasse. Finally, any Dedekind–Hasse norm makes $\mathcal O$ a PID by @[the Dedekind–Hasse criterion]mt4-dedekind-hasse-pid, so the same argument applies to $H$.
