**Correct choice: (B).**

**Fastest valid route.** Work with unordered pairs. There are $\binom72=21$ pairs in total, of which $\binom32=3$ are all blue. Thus $18$ pairs satisfy the condition “at least one red.” Of those, $\binom42=6$ are all red, so the conditional probability is $6/18=1/3$.

**Verification.** Directly,

$$
P(RR)=\frac{\binom42}{\binom72}=\frac27,
\qquad
P(\text{at least one }R)=1-\frac{\binom32}{\binom72}=\frac67.
$$

Therefore

$$
P(RR\mid\text{at least one }R)=\frac{2/7}{6/7}=\frac13.
$$
