$\lor E$ requires two subproofs: one deriving a common conclusion $C$ from assumption $A$, and another deriving that same $C$ from assumption $B$. The proposed proof supplies only the $A$ case. Once that subproof closes, its occurrence of $A$ cannot be used independently.

For a semantic counterinstance, take $A=p$ and $B=q$ for distinct atoms and set $v(p)=0$, $v(q)=1$. Then $p\lor q$ is true while $p$ is false, so $p\lor q\not\models p$. Soundness therefore confirms that no generally valid derivation schema of the proposed form exists.
