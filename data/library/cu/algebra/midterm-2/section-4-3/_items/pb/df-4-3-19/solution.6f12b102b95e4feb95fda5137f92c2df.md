**Step 1: partition K by H-conjugacy.** Every $G$-conjugate of $x$ lies in $H$ by normality. Conjugating such an element by $H$ keeps it in $K$, so $K$ is partitioned into $H$-conjugacy classes.

**Step 2: show these classes have equal size.** For $g\in G$, conjugation by $g$ sends the $H$-class of $x$ onto the $H$-class of $gxg^{-1}$:

$$
g\{hxh^{-1}:h\in H\}g^{-1}=\{h'(gxg^{-1})h'^{-1}:h'\in H\}.
$$

The equality uses $gHg^{-1}=H$. This map is a bijection, with inverse conjugation by $g^{-1}$. Since every element of $K$ is some $gxg^{-1}$, all $H$-classes in $K$ have equal cardinality.

**Step 3: count the H-classes using an action.** The group $G$ acts transitively on this collection of classes by conjugation. A group element $g$ stabilizes the class of $x$ exactly when $gxg^{-1}=hxh^{-1}$ for some $h\in H$. This equality is equivalent to $h^{-1}g\in C_G(x)$, or $g\in HC_G(x)$. Conversely any $g=hc$ with $c\in C_G(x)$ sends $x$ to $hxh^{-1}$ and stabilizes its $H$-class. Thus the stabilizer is $HC_G(x)$, a subgroup because $H$ is normal. Orbit–stabilizer gives the number of $H$-classes as $[G:HC_G(x)]$. This argument also works for infinite groups and avoids cancellation of infinite cardinalities.

**Step 4: specialize to Aₙ.** For $n\ge2$, $A_n\nsubg S_n$ has index $2$. The subgroup $A_nC_{S_n}(x)$ lies between $A_n$ and $S_n$, so it is either $A_n$ or $S_n$. Its index is therefore $2$ or $1$. The previous steps say the $S_n$-class splits into exactly that many equally sized $A_n$-classes. For $n=1$, both groups are trivial and there is one class.

**Technique:** regard the smaller conjugacy classes themselves as points of an action. This is the normal-subgroup orbit argument from 4.1.9.

**Foundations:** @cu:algebra:midterm-2:theorems:th:orbit-stabilizer, @cu:algebra:midterm-2:definitions:df:normalizer-centralizer.
