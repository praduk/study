A probability space is a @math:analysis:measure-construction:df:measure-space $(\Omega,\mathcal F,\mathbb P)$ with $\mathbb P(\Omega)=1$. The points of $\Omega$ are outcomes and members of the @[sigma algebra]math:analysis:measure-construction:df:measure-space $\mathcal F$ are events. An event is almost sure when its probability is one; an event of probability zero is null. A null event need not be empty.

For events $A,B$ with $\mathbb P(B)>0$, conditional probability is $\mathbb P(A\mid B)=\mathbb P(A\cap B)/\mathbb P(B)$. This formula does not define conditioning on a null event or on a continuously valued observation; those require additional constructions.

For a finite sample space, weights $p_\omega\ge0$ with $\sum_\omega p_\omega=1$ give $\mathbb P(A)=\sum_{\omega\in A}p_\omega$. More generally probability need not have a density with respect to a chosen coordinate volume.
