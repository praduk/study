Suppose $\Gamma\cup\{A\}\vdash B$. Place that finite derivation inside a subproof whose temporary assumption is $A$, while retaining the used members of $\Gamma$ as outer premises. The subproof ends in $B$, so $\to I$ discharges $A$ and yields $A\to B$ from $\Gamma$.

Conversely, suppose $\Gamma\vdash A\to B$. By weakening, $\Gamma\cup\{A\}\vdash A\to B$. The added premise gives $\Gamma\cup\{A\}\vdash A$. Applying $\to E$ yields $\Gamma\cup\{A\}\vdash B$.
