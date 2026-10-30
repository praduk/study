**Technique trigger:** assume simplicity → restrict the Sylow number → apply $(N)^+$ → obtain a normal subgroup or a subgroup of impossibly small index.

**Definitions and results used:** @[Simple groups]cu:algebra:midterm-3:foundations:df:mt3-simple and @[abelian simple groups have prime order]cu:algebra:midterm-3:foundations:th:mt3-abelian-simple; @[Faithful actions of nonabelian simple groups into alternating groups]cu:algebra:midterm-3:foundations:th:mt3-simple-actions; @[Sylow's theorem]cu:algebra:midterm-3:sylow:th:mt3-sylow, @[unique Sylow subgroups are normal]cu:algebra:midterm-3:sylow:th:mt3-sylow-normality, and @[the Sylow (N)+ corollary]cu:algebra:midterm-3:sylow:th:mt3-intersection; @[Index-two normality]cu:algebra:midterm-3:foundations:th:mt3-index-two, @[normalizers]cu:algebra:midterm-3:foundations:df:mt3-normalizer, and @[Lagrange's theorem]cu:algebra:midterm-3:foundations:th:mt3-lagrange.

**(a)** Because $|G|=120$ is composite, simplicity would make $G$ nonabelian. Sylow gives

$$
120=2^3\cdot15,\qquad n_2\mid15,\qquad n_2\equiv1\pmod2,
$$

so $n_2\in\{1,3,5,15\}$. A value $1$ would give a proper nontrivial normal subgroup of order $8$.

For $n_2>1$, conjugation on the Sylow subgroups is a nontrivial transitive action. Its kernel is normal, so simplicity makes the action faithful. Composing with the sign map gives a homomorphism $G\to C_2$; it must be trivial, since a nontrivial one would be injective by simplicity, impossible for a group of order $120$. Thus the faithful image lies in $A_{n_2}$.

The values $3$ and $5$ are impossible: $|A_3|=3$ and $|A_5|=60$, both smaller than $120$. Therefore $n_2=15$.

**(b)** Since $15\not\equiv1\pmod4$, the corollary gives distinct Sylow $2$-subgroups with

$$
[P:P\cap Q]=[Q:P\cap Q]=2.
$$

Each has order $8$, so $D=P\cap Q$ has order $4$.

**(c)** Index-two normality gives $D\trianglelefteq P,Q$, and therefore $P,Q\le N_G(D)$. Since $P\ne Q$, this normalizer strictly contains $P$. Its order is a multiple of $8$, greater than $8$, and divides $120$. Consequently

$$
|N_G(D)|\in\{24,40,120\}.
$$

**(d)** If the order is $120$, then $D\trianglelefteq G$, contradicting simplicity because $1<|D|=4<120$.

If the order is $24$, the normalizer has index $5$. The faithful coset action of the nonabelian simple group would embed $G$ in $A_5$, impossible because $120>60$.

If the order is $40$, its index is $3$, giving the equally impossible embedding $G\hookrightarrow A_3$.

All possibilities fail, so no group of order $120$ is simple.

**Common trap:** $120$ does divide $|S_5|=120$. Merely embedding in $S_5$ is not a contradiction. The sign argument, which puts the image in $A_5$, is essential to this proof.
