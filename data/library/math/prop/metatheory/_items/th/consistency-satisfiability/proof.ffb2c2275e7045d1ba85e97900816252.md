If $\Gamma$ is satisfiable, some valuation satisfies all its members. Were $\Gamma\vdash\false$, soundness would force that valuation to satisfy $\false$, impossible. Hence $\Gamma$ is consistent.

If $\Gamma$ is unsatisfiable, then every valuation satisfying $\Gamma$ satisfies $\false$ vacuously, so $\Gamma\models\false$. Strong completeness gives $\Gamma\vdash\false$, making $\Gamma$ inconsistent. Taking the contrapositive, consistency implies satisfiability. Together the directions prove the equivalence.
