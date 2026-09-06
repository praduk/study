The supremum of the empty set of ordinals is $0$, so
$\operatorname{rank}(\varnothing)=0$. Therefore

$$
\operatorname{rank}(\{\varnothing\})=0+1=1.
$$

For $x=\{\varnothing,\{\varnothing\}\}$, the two contributions are $1$ and $2$, so $\operatorname{rank}(x)=2$.

Each finite ordinal $n$ has rank $n$, by induction. Hence

$$
\operatorname{rank}(\omega)=\sup_{n<\omega}(n+1)=\omega.
$$

Every $X\subseteq\omega$ has rank at most $\omega$, since its elements are finite ordinals. The member $\omega\in\mathcal{P}(\omega)$ itself has rank $\omega$. Thus

$$
\operatorname{rank}(\mathcal{P}(\omega))
=\sup_{X\subseteq\omega}(\operatorname{rank}(X)+1)
=\omega+1.
$$
