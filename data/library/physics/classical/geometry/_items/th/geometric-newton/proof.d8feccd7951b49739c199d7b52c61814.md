In a chart, $L=\tfrac12g_{ij}\dot q^i\dot q^j-V$. Its Euler–Lagrange expression is

$$
g_{ij}\ddot q^j+\partial_k g_{ij}\dot q^k\dot q^j-\tfrac12\partial_i g_{jk}\dot q^j\dot q^k+\partial_iV=0.
$$

Multiply by $g^{\ell i}$ and symmetrize the coefficient of $\dot q^j\dot q^k$. The connection formula in @math:diffgeo:connections:th:levi-civita gives

$$
\ddot q^\ell+\Gamma^\ell_{jk}\dot q^j\dot q^k=-g^{\ell i}\partial_iV.
$$

These are the components of the claimed vector identity. Conversely, multiplying this identity by $g_{i\ell}$ recovers every Euler–Lagrange equation. The zero-potential case is the defining affine geodesic equation in @math:diffgeo:geodesics:df:geodesic.
