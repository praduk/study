**Correct choice: (B).**

**Fastest valid route.** Begin with all $3^5$ functions and use inclusion-exclusion on the codomain values that are missed:

$$
3^5-\binom31 2^5+\binom32 1^5=243-96+3=150.
$$

**Verification.** Missing a specified codomain value leaves $2^5$ functions, so subtract $3\cdot2^5$. A function whose image is a specified single value was subtracted twice and must be added back; there are $3$ such constant functions. A function cannot miss all three codomain values. The total is therefore $150$.
