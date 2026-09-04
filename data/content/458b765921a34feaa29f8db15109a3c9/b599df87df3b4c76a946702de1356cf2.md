A **literal** is an atom $p$ or its negation $\neg p$. A **term** is a finite conjunction of literals, and a **clause** is a finite disjunction of literals. For a nonempty list $L_1,\ldots,L_n$, define right-associated formulas from the right by

$$W_n=L_n,\quad W_j=(L_j\land W_{j+1}),\qquad V_n=L_n,\quad V_j=(L_j\lor V_{j+1})\quad(1\leq j<n),$$

and abbreviate $W_1$ by $\bigwedge_{i=1}^nL_i$ and $V_1$ by $\bigvee_{i=1}^nL_i$. For $n=0$, the empty conjunction is $\true$ and the empty disjunction is $\false$.

Fix $P=\{p_1,\ldots,p_n\}$ and a finite assignment $a:P\to\{0,1\}$. The associated **minterm** is

$$m_a=\bigwedge_{i=1}^n \ell_i,\qquad \ell_i=\begin{cases}p_i&a(p_i)=1,\\\neg p_i&a(p_i)=0.\end{cases}$$

For every total valuation $v$, $v\models m_a$ exactly when $v|_P=a$; equivalently, among assignments on $P$, only $a$ satisfies $m_a$. The associated **maxterm** is

$$k_a=\bigvee_{i=1}^n d_i,\qquad d_i=\begin{cases}\neg p_i&a(p_i)=1,\\p_i&a(p_i)=0.\end{cases}$$

For every total valuation $v$, $v\not\models k_a$ exactly when $v|_P=a$; equivalently, among assignments on $P$, only $a$ falsifies $k_a$.
