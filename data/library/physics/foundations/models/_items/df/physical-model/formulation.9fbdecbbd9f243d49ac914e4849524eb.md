A deterministic model consists of a state space $X$, parameters $\theta\in\Theta$, an evolution rule, and an observation map $O:X\times\Theta\to Y$. Initial data select a state trajectory; parameters specify the model rather than the instantaneous preparation. A stochastic model instead supplies @[conditional probability]math:analysis:probability-basics:df:probability-space laws for observations or trajectories.

For a point particle, position and velocity can be state coordinates, mass a parameter, and a measured flight time an observable. The correspondence between a physical preparation and a state is part of the model. Changing coordinates on $X$ does not by itself change a prediction.

For smooth finite-dimensional models, make this distinction intrinsic using @physics:foundations:geometric-models:df:geometric-state. A state is a point of a manifold, observables are functions, and dynamics is a vector field; coordinates are a representation of these objects.
