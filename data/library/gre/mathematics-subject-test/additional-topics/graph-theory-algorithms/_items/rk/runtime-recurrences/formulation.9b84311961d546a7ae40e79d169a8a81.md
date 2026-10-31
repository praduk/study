For $n$ a power of two and constant positive base cost, $T(n)=T(n/2)+\Theta(1)$ gives $\Theta(\log n)$; $T(n)=2T(n/2)+\Theta(n)$ gives $\Theta(n\log n)$. Count work per level and the number of levels. More generally leaves can dominate, as in $T(n)=2T(n/2)+\Theta(1)=\Theta(n)$.

**Pattern practice.** @gre:mathematics-subject-test:additional-topics:graph-theory-algorithms:pb:divide-conquer-recurrence; @gre:mathematics-subject-test:additional-topics:graph-theory-algorithms:pb:constant-branch-work.
