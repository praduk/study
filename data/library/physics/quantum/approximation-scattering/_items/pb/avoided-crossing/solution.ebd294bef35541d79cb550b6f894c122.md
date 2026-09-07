The characteristic polynomial is $E^2-\Delta E-g^2$, so


$$
E_\pm=\frac{\Delta\pm\sqrt{\Delta^2+4g^2}}2.
$$


For $g\ne0$, corresponding normalized eigenvectors are

$$
v_\pm=\frac{(g,E_\pm)^T}{\sqrt{g^2+E_\pm^2}}.
$$

Multiplication by $H$ verifies the eigenvalue equations using $E_\pm^2=\Delta E_\pm+g^2$. Their inner product vanishes because $E_+E_-=-g^2$. Thus the orthogonal matrix with columns $v_-,v_+$ diagonalizes $H$ to $\operatorname{diag}(E_-,E_+)$. For $g=0$, use the standard basis, with $E_-=0$ and $E_+=\Delta$.

For $\Delta>0$, the Taylor expansion $\sqrt{1+x}=1+x/2+O(x^2)$ with $x=4g^2/\Delta^2$ gives $E_-=-g^2/\Delta+O(g^4/\Delta^3)$. The correction lowers the unperturbed ground energy. This expansion assumes $|g|/\Delta\ll1$; as the gap closes that ratio ceases to be small. At $\Delta=0$ the exact eigenvalues are $\pm|g|$, so the nondegenerate expansion is inappropriate.
