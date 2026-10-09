A composition series is a chain from $1$ to the group in which each term is normal in the next and every successive quotient is nontrivial simple. A group of order $2$ is simple, so every normal step of index $2$ is already a composition step.

**Q₈.** Its unique order-$2$ subgroup is $Z=\langle-1\rangle$. Its three order-$4$ subgroups are $\langle i\rangle,\langle j\rangle,\langle k\rangle$, each cyclic. The three series are

$$
1<Z<\langle i\rangle<Q_8,
$$


$$
1<Z<\langle j\rangle<Q_8,
$$


$$
1<Z<\langle k\rangle<Q_8.
$$

In each chain all steps have index $2$ and hence are normal. Every factor is $C_2$.

**D₈.** Let $R=\langle r\rangle$, $A=\langle r^2,s\rangle$, and $B=\langle r^2,sr\rangle$. These are the three order-$4$ subgroups; $R\cong C_4$ and $A,B\cong V_4$. The seven series are

$$
1<\langle r^2\rangle<R<D_8,
$$


$$
1<\langle r^2\rangle<A<D_8,
$$


$$
1<\langle s\rangle<A<D_8,
$$


$$
1<\langle sr^2\rangle<A<D_8,
$$


$$
1<\langle r^2\rangle<B<D_8,
$$


$$
1<\langle sr\rangle<B<D_8,
$$


$$
1<\langle sr^3\rangle<B<D_8.
$$

Again all factors in every series are $C_2$, in the order $C_2,C_2,C_2$ from bottom to top. The order-$2$ term need only be normal in its immediate order-$4$ overgroup; reflection subgroups need not be normal in all of $D_8$.

**Why these are all.** In either group, a composition factor has order $2,4$, or $8$, since its order divides $8$. No group of order $4$ is simple: Cauchy's theorem gives a subgroup of order $2$, which has index $2$ and is normal. Neither $Q_8$ nor $D_8$ is simple, since each has proper normal subgroups of index $2$. Thus no composition step can skip from order $1$ to $4$, from $2$ to $8$, or from $1$ to $8$. The series must pass through orders $1,2,4,8$. The lists above exhaust all choices at those orders.

**Technique:** enumerate maximal normal subgroups, then work down inside each one. Normality is required between adjacent terms, not necessarily in the whole group.

**Foundations:** @cu:algebra:midterm-2:definitions:df:simple-composition, @cu:algebra:midterm-2:theorems:th:jordan-holder, @cu:algebra:midterm-2:theorems:th:derived-solvability.
