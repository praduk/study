The **Kuratowski ordered pair** is

$$
\langle a,b\rangle=\{\{a\},\{a,b\}\}.
$$

For sets $A$ and $B$, their **Cartesian product** is

$$
A\times B=\{z:\exists a\in A\,\exists b\in B\,(z=\langle a,b\rangle)\}.
$$

This is a set: every Kuratowski pair with $a\in A$ and $b\in B$ lies in
$\mathcal{P}(\mathcal{P}(A\cup B))$, and Separation selects exactly the desired pairs. Higher tuples may be defined by iteration, for example
$\langle a,b,c\rangle=\langle\langle a,b\rangle,c\rangle$.
