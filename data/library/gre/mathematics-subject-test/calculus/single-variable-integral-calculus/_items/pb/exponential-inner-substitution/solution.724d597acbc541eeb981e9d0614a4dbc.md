**Correct choice: (B).**

**Pattern cue.** The derivative of the expression inside the exponential appears with the opposite sign.

**Fast route.** Put $u=\cos x$, so $du=-\sin x\,dx$. As $x$ goes from $0$ to $\pi/2$, $u$ goes from $1$ to $0$. Thus

$$
\int_0^{\pi/2}\sin x\,e^{\cos x}\,dx
=-\int_1^0e^u\,du
=\int_0^1e^u\,du=e-1.
$$

**Check.** An antiderivative is $-e^{\cos x}$. Its endpoint difference is $-1-(-e)=e-1$, which is positive, as the integrand requires.

**Trap.** Transform both the differential and the endpoints. Reversing the endpoints already supplies a minus sign; do not apply it twice.
