**Strategy.** Translate “common multiple” into membership in $(a)\cap(b)$. For (a) and (b), determine when that intersection has a generator. For the formula in (c), use a Bézout identity to prove the proposed element divides every common multiple.

**(a) Characterize the largest principal ideal.** By @[divisibility]mt4-divisibility-gcd, $x$ is a common multiple exactly when $x\in(a)\cap(b)$. If $e$ is an @[lcm]mt4-lcm, it belongs to this intersection and divides every element in it. These two facts give the two inclusions in $(e)=(a)\cap(b)$. In particular $(e)$ is the largest principal ideal in the intersection.

Conversely, suppose $(e)$ is the largest principal ideal contained there. Then $e$ is a common multiple. Every common multiple $x$ generates another principal ideal contained there, so $(x)\subseteq(e)$. Hence $e\mid x$, the remaining lcm condition.

**(b) Prove existence and uniqueness in a Euclidean domain.** The intersection is an @[ideal]mt4-ideal because differences and ring multiples stay in both ideals. It contains $ab\ne0$ since a Euclidean domain is an @[integral domain]mt4-integral-domain. By @[the Euclidean principal ideal theorem]mt4-euclidean-principal, the intersection has a generator. By (a), its generators are exactly the lcms. In a domain, two generators of the same ideal differ by a unit by @[Exercise 7.4.8]mt4-7-4-8.

**(c) Verify $ab/d$ is an lcm.** Write $a=da'$ and $b=db'$. The @[Euclidean algorithm]mt4-euclidean-gcd expresses a gcd as a linear combination of $a,b$. Since any other gcd differs by a unit by @[the gcd generator criterion]mt4-gcd-generated-pair, our chosen $d$ also has the form $d=ax+by$. Substitute and @[cancel]mt4-cancellation the nonzero $d$ to get $1=a'x+b'y$.

- **It is a common multiple.** The proposed element $e=da'b'=ab/d$ equals both $ab'$ and $ba'$.
- **It divides every common multiple.** Given a common multiple $m$, write $m=bu=av$. Then $ma'=eu$ and $mb'=ev$. Multiplying the identity $1=a'x+b'y$ by $m$ gives $m=e(ux+vy)$. Thus $e\mid m$, as required.
