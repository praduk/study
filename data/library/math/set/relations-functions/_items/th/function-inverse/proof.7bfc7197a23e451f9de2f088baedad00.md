Suppose $f$ is bijective. For each $b\in B$, surjectivity supplies an $a\in A$ with $f(a)=b$, and injectivity makes that $a$ unique. Define $g(b)$ to be this unique $a$. Replacement gives the graph of $g$. Then $g(f(a))=a$ and $f(g(b))=b$, so both composite identities hold.

Conversely, suppose such a $g$ exists. If $f(a)=f(a')$, applying $g$ gives
$a=g(f(a))=g(f(a'))=a'$, so $f$ is injective. For each $b\in B$, take $a=g(b)$; then $f(a)=f(g(b))=b$, so $f$ is surjective.

If $g$ and $h$ are both inverses, then
$g=g\circ\mathrm{id}_B=g\circ(f\circ h)=(g\circ f)\circ h=\mathrm{id}_A\circ h=h$. Hence the inverse is unique.
