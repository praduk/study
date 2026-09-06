Suppose $\Gamma\models A$. If a valuation $v$ satisfied $\Gamma\cup\{\neg A\}$, then $v\models\Gamma$, so $v\models A$ by consequence. But $v\models\neg A$ also says $v\not\models A$, a contradiction. Hence the enlarged set is unsatisfiable.

Conversely, suppose $\Gamma\cup\{\neg A\}$ is unsatisfiable. Let $v$ satisfy $\Gamma$. If $v$ did not satisfy $A$, the classical negation clause would give $v\models\neg A$, so $v$ would satisfy the enlarged set. That is impossible. Thus every valuation satisfying $\Gamma$ satisfies $A$, and $\Gamma\models A$.
