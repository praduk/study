For $r=|x|>0$, $\nabla\cdot(xr^{-3})=3r^{-3}-3r^{-5}|x|^2=0$. On a sphere of radius $\epsilon$, $j\cdot n=q/(4\pi\epsilon^2)$, so the outward flux is $q$.

For a test function $f$, integrate $\nabla\cdot(fj)=j\cdot\nabla f$ on the complement of the radius-$\epsilon$ ball, truncating outside the support of $f$. Its inner boundary normal points inward, so $-\int_{|x|>\epsilon}j\cdot\nabla f=q\,(4\pi\epsilon^2)^{-1}\int_{|x|=\epsilon}f\,dA$. The right side tends to $qf(0)$, and the locally integrable field permits the left limit. This is the distributional assertion.
