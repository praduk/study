For any valuation, either $p$ is false, in which case $p\to q$ is true, or $p$ is true. In the latter case, if $q$ is true then $q\to p$ is true, while if $q$ is false then $q\to p$ is still true because its antecedent is false. Thus the disjunction is always true.

For a formal proof, use the derived theorem $p\lor\neg p$ and $\lor E$.

- In the $p$ case, assume $q$, reiterate $p$, and use $\to I$ to get $q\to p$. Then infer $(p\to q)\lor(q\to p)$ by $\lor I$.
- In the $\neg p$ case, assume $p$, derive $\false$, use $\false E$ to obtain $q$, and close by $\to I$ to get $p\to q$. Then infer the target disjunction by $\lor I$.

Both cases yield the target, so $\lor E$ discharges them. No premises remain.
