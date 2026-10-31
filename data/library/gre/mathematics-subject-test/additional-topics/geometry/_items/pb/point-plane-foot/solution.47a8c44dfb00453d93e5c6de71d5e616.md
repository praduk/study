**Answer.** Distance $1/3$; foot $(16/9,10/9,34/9)$.

**Pattern cue.** Use the plane residual and the normal vector; normalize differently for distance and projection.

**Fast route.** The normal is $\mathbf n=(2,-1,2)$, with $\|\mathbf n\|=3$ and $\|\mathbf n\|^2=9$. The signed residual at $Q$ is $4-1+8-10=1$, so distance is $|1|/3$. The foot is $Q-\mathbf n/9=(16/9,10/9,34/9)$. Substitution gives $2(16/9)-10/9+2(34/9)=10$, and the displacement is parallel to the normal.

**Trap.** Subtract residual divided by squared normal length when finding the foot; dividing only by normal length gives the wrong point.

**Recall.** @gre:mathematics-subject-test:additional-topics:geometry:rk:planes-three-dimensions.
