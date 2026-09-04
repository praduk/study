For every formula $\varphi(x,y,p_1,\ldots,p_n)$, if it defines a unique output $y$ for each input $x\in A$, then those outputs form a set. Formally, the corresponding instance is

$$
\forall A\left[
\bigl(\forall x\in A\,\exists!y\,\varphi(x,y,\vec p)\bigr)
\to
\exists B\,\forall y\,
\bigl(y\in B\leftrightarrow\exists x\in A\,\varphi(x,y,\vec p)\bigr)
\right].
$$

Replacement is essential when a definable operation is iterated through an arbitrary set-sized ordinal. It implies the corresponding Collection principle in ZF.
