**Strategy.** When $\beta$ does not divide $\alpha$, the Dedekind–Hasse condition asks for a nonzero element of $(\alpha,\beta)$ with smaller norm than $\beta$. Try a generator $\gamma$ of this ideal. Show that the quotient $\beta/\gamma$ is a nonunit, then use multiplicativity to get the strict decrease.

**Check the norm properties.** The @[quadratic norm formula]mt4-quadratic-integers-norm and the @[quadratic norm and unit criterion]mt4-quadratic-norm-units show that $H=|N|$ vanishes at $0$, takes positive integer values on nonzero elements, and is multiplicative. In particular a nonzero nonunit has $H$-value at least $2$.

**Produce the smaller element.** Let $\alpha,\beta\ne0$ with $\beta\nmid\alpha$. Since $\mathcal O$ is a @[PID]mt4-pid, write $(\alpha,\beta)=(\gamma)$. Then $\gamma\ne0$, and @[Bézout’s identity]mt4-pid-bezout expresses $\gamma$ as a linear combination of $\alpha$ and $\beta$.

Since $\beta\in(\gamma)$, write $\beta=t\gamma$. If $t$ were a unit, $\beta$ and $\gamma$ would be @[associates]mt4-associates, so $\alpha\in(\gamma)=(\beta)$. This contradicts $\beta\nmid\alpha$. Thus $t$ is a nonzero nonunit, and hence

$$
H(\beta)=H(t)H(\gamma)\ge 2H(\gamma)>H(\gamma)>0.
$$

This is exactly the required smaller element. When $\beta\mid\alpha$, the other clause of the @[Dedekind–Hasse definition]mt4-dedekind-hasse already holds. Thus $H$ works for every pair.

**Deduce the last assertion.** If $\mathcal O$ admits any Dedekind–Hasse norm, the @[Dedekind–Hasse criterion]mt4-dedekind-hasse-pid makes it a PID. The argument above then shows that its particular norm $H=|N|$ works.
