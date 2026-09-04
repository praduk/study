Let $I=\alpha\cap\beta$. It is an initial segment of both ordinals. To see this for $\alpha$, if $x\in I$ and $y\in x$, then transitivity of both $\alpha$ and $\beta$ puts $y$ in both, hence in $I$.

Every proper initial segment $I$ of an ordinal $\alpha$ equals one of its members. Indeed, let $\gamma$ be the $\in$-least member of $\alpha\setminus I$. All $\delta\in\gamma$ lie in $I$ by minimality. Conversely, if $\delta\in I$, linearity in $\alpha$ compares $\delta$ and $\gamma$. We cannot have $\delta=\gamma$, and if $\gamma\in\delta$, initiality of $I$ would put $\gamma$ in $I$. Thus $\delta\in\gamma$. Hence $I=\gamma\in\alpha$.

Apply this to $I=\alpha\cap\beta$. If $I$ is proper in both, then $I\in\alpha$ and $I\in\beta$, so $I\in\alpha\cap\beta=I$, impossible because $\in$ is irreflexive on an ordinal. Therefore $I$ equals at least one of $\alpha,\beta$. If it equals both, $\alpha=\beta$. If $I=\alpha\ne\beta$, then $\alpha$ is a proper initial segment of $\beta$, so $\alpha\in\beta$; symmetrically for the other case.

The cases are mutually exclusive by irreflexivity, asymmetry, and Extensionality. The subset characterization follows because ordinals are transitive and the three cases are exhaustive.
