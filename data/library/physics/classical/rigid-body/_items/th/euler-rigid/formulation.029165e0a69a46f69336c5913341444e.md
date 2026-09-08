Assume angular-momentum balance about the center of mass for a rigid body, with body torque $\tau_b$ and constant inertia $I$. Then

$$
I\dot\omega+\omega\times(I\omega)=\tau_b.
$$

In principal axes this reads $I_1\dot\omega_1+(I_3-I_2)\omega_2\omega_3=\tau_1$, with cyclic analogues. Torque-free motion preserves both $\omega^TI\omega/2$ and $|I\omega|^2$.

For @[positive definite]math:algebra:linear-foundations:df:bilinear-forms inertia, regard $Q=\SO(3)$ as the configuration manifold. At $R$, identify $\dot R$ with its body angular velocity through $R^{-1}\dot R=\widehat\omega$, where $\widehat\omega x=\omega\times x$. The kinetic metric is $g_R(\dot R_1,\dot R_2)=\omega_1^TI\omega_2$; it is invariant under multiplying $R$ on the left by a fixed rotation. Torque-free motion is its affine geodesic flow by @physics:classical:geometry:th:geometric-newton. The body components of the tangent vector use a moving frame, which is why their equation includes $\omega\times(I\omega)$ even when torque vanishes. The spatial angular momentum remains the rotation momentum in @physics:classical:geometry:df:moment-map.
