**Definitions and results used:** @[Unique, normal, and characteristic Sylow subgroups]cu:algebra:midterm-3:sylow:th:mt3-sylow-normality; @[Characteristic subgroups and normality]cu:algebra:midterm-3:foundations:th:mt3-characteristic-normal; @[Normalizer]cu:algebra:midterm-3:foundations:df:mt3-normalizer.

**Technique:** Replace a normal Sylow subgroup by a characteristic subgroup; apply the result inside the next normalizer.

Because $P$ is normal in $H$, it is the unique Sylow $p$-subgroup of $H$. Every automorphism of $H$ therefore preserves $P$, so $P$ is characteristic in $H$. Characteristic-in-normal implies normal, giving $P\nsubg K$.

For the deduction, put $K=N_G(H)$. Then $H\nsubg K$, $P\nsubg H$, and $P\in\Syl_p(H)$, so the first part gives $P\nsubg K$. Thus $K\le N_G(P)=H$. The reverse containment $H\le N_G(H)=K$ always holds. Hence $\boxed{N_G(N_G(P))=N_G(P)}$.
