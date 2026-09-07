Remove a measurable null exceptional set $N$. For positive integers $k,m$, put
$E_{k,m}=\bigcup_{n\ge m}\{|f_n-f|>1/k\}\setminus N$.
For fixed $k$ these sets decrease to the empty set, so their measures tend to zero by finiteness. Choose $m_k$ with $\mu(E_{k,m_k})<\delta/2^{k+1}$. Set $E=N\cup\bigcup_k E_{k,m_k}$. Then $\mu(E)<\delta$. Given $\epsilon>0$, choose $k$ with $1/k<\epsilon$. For all $n\ge m_k$ and all $x\notin E$, $|f_n(x)-f(x)|\le1/k<\epsilon$, which is uniform convergence.
