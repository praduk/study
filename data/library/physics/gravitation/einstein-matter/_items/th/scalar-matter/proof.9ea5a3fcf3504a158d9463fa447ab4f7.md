At fixed metric, the field variation is $-c^{-1}\int(\partial^\mu\varphi\partial_\mu\delta\varphi+V'\delta\varphi)\sqrt{-g}\,d^4x$. Integration by parts gives $c^{-1}\int(\Box_g\varphi-V')\delta\varphi\sqrt{-g}\,d^4x$. Arbitrary compact variations give the equation and its converse.

For inverse-metric variation, differentiate the explicit $g^{\mu\nu}$ and use $\delta\sqrt{-g}=-\tfrac12\sqrt{-g}g_{\mu\nu}\delta g^{\mu\nu}$. The coefficient of $-\delta g^{\mu\nu}/(2c)$ is precisely the displayed $T_{\mu\nu}$.

Finally the product rule gives

$$
\nabla_\mu T^{\mu}{}_{\nu}=(\Box_g\varphi)\partial_\nu\varphi+\partial^\mu\varphi\nabla_\mu\partial_\nu\varphi-\tfrac12\nabla_\nu(\partial_\alpha\varphi\partial^\alpha\varphi)-V'\partial_\nu\varphi.
$$

The middle two terms cancel by metric compatibility and symmetry of the scalar @[Hessian]math:uganalysis:metric-multivariable:df:hessian. The remainder is $(\Box_g\varphi-V')\partial_\nu\varphi$, zero on shell.
