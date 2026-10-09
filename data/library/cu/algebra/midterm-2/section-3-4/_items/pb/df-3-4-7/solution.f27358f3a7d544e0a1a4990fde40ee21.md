**Step 1: take series on the two sides of H.** Every finite group has a composition series: if it is nontrivial, select a maximal proper normal subgroup, whose quotient is simple, and continue inside that subgroup. Strictly decreasing finite orders guarantee termination. Apply this construction to $H$ and to $G/H$.

Write a composition series of $H$ as

$$
1=H_0\nsubg H_1\nsubg\cdots\nsubg H_t=H.
$$

Write one of $G/H$ as

$$
1=\bar K_0\nsubg\bar K_1\nsubg\cdots\nsubg\bar K_s=G/H.
$$


**Step 2: pull the quotient series back.** Let $\pi:G\to G/H$ be projection and define $K_i=\pi^{-1}(\bar K_i)$. Then $K_0=H$, $K_s=G$, and $K_i\le K_{i+1}$. To check adjacent normality, take $k\in K_{i+1}$ and $a\in K_i$. Their images satisfy $\pi(k)\pi(a)\pi(k)^{-1}\in\bar K_i$, so $kak^{-1}\in K_i$. Thus $K_i\nsubg K_{i+1}$.

The map $K_{i+1}\to\bar K_{i+1}/\bar K_i$, sending $k$ to $\pi(k)\bar K_i$, is surjective and has kernel $K_i$. Hence

$$
K_{i+1}/K_i\cong\bar K_{i+1}/\bar K_i,
$$

which is simple. Every pulled-back step is therefore a composition step.

**Step 3: concatenate.** The chain

$$
1=H_0\nsubg\cdots\nsubg H_t=H=K_0\nsubg\cdots\nsubg K_s=G
$$

is the desired series. Count the shared term $H=K_0$ only once. If $H=1$ or $H=G$, the corresponding series is empty on that side, and the argument still works.

**Technique:** construct inside the normal subgroup and inside the quotient, then lift and concatenate.

**Foundations:** @cu:algebra:midterm-2:definitions:df:simple-composition, @cu:algebra:midterm-2:theorems:th:jordan-holder, @cu:algebra:midterm-2:theorems:th:derived-solvability.
