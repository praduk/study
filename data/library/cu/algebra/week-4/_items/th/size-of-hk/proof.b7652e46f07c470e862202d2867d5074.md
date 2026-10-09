Let $H$ act on $G/K$ by left multiplication:
$$
\begin{aligned}
\cdot: H \times G/K &\to G/K \\
(h, gK) &\mapsto hgK.
\end{aligned}
$$

Note that
$$
HK = \union_{h\in H} hK = \union_{hK\in \Orb_H(K)} hK.
$$

Because multipication by $h$ is a bijection, the number of elements is therefore the number of orbits times the size of each orbit
$$
|HK| = |\Orb_H(K)| | K |.
$$

By Orbit-Stabilizer,
$$
|\Orb_H(K)| = [H:\Stab_H(K)].
$$

Note that
$$
\begin{aligned}
\Stab_H(K) &= \set{h\in H : hK=1K} \\
&= \set{h\in H : h\in K} \\
&= H\cap K.
\end{aligned}
$$

So
$$
|HK| = |\Orb_H(K)||K| = \frac{|H||K|}{|H\cap K|}.
$$
