**Correct choice: (B).**

**Fast route.** Each recursion level performs total work $n$, and there are $\log_2n$ levels, giving $\Theta(n\log n)$.

**Trap check.** Two subproblems double the count as their size halves; the work per level stays linear.
