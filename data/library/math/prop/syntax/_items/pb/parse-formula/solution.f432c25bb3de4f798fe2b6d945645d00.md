The main connective is $\leftrightarrow$. The left child is $\neg(p\land(q\to r))$ and the right child is $(p\lor q)\to r$.

The distinct subformulas are

$$p,\ q,\ r,\ q\to r,\ p\land(q\to r),\ \neg(p\land(q\to r)),\ p\lor q,\ (p\lor q)\to r,\ F.$$

Thus there are nine distinct subformulas. Counting tree nodes instead gives twelve occurrences: the whole formula contributes one; its left subtree has six nodes; and its right subtree has five nodes.

The ranks from the bottom up are

$$\operatorname{rk}(q\to r)=1,\quad \operatorname{rk}(p\land(q\to r))=2,\quad \operatorname{rk}(\neg(p\land(q\to r)))=3,$$

$$\operatorname{rk}(p\lor q)=1,\quad \operatorname{rk}((p\lor q)\to r)=2.$$

Therefore $\operatorname{rk}(F)=1+\max\{3,2\}=4$, and $\operatorname{At}(F)=\{p,q,r\}$.
