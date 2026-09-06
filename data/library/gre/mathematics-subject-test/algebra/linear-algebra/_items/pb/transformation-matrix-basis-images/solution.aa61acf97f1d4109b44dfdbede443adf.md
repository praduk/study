**Fastest valid route.** Compute only the three basis images and place their coordinate vectors in columns:

$$T(1)=0,\qquad T(x)=1,\qquad T(x^2)=(x+1)^2-x^2=1+2x.$$

Their $\mathcal B$-coordinates are $(0,0,0)^T$, $(1,0,0)^T$, and $(1,2,0)^T$. Hence

$$[T]_{\mathcal B}=\begin{pmatrix}0&1&1\\0&0&2\\0&0&0\end{pmatrix}.$$

The answer is **(B)**. Choice (A) is the tempting transpose error.
