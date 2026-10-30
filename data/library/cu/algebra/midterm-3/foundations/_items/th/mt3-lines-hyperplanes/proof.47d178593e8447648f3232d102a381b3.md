**Definitions used:** @mt3-linear.

Every line contains $p-1$ nonzero vectors; distinct lines have disjoint nonzero vectors. Thus the line count is $(p^r-1)/(p-1)$.

A functional is determined by its $r$ values on a basis, so there are $p^r-1$ nonzero functionals. Each nonzero functional is onto $\F_p$ and its kernel is a hyperplane. Conversely, choose a basis of a hyperplane and extend it by one vector; taking the final coordinate defines a functional with precisely that kernel. If two nonzero functionals have the same kernel, choose a vector where the first is $1$ and compare values on its scalar multiples and the common kernel: the second is a nonzero scalar multiple of the first. Hence exactly $p-1$ functionals give each hyperplane.

Finally, extend a given nonzero vector to a basis. The span of the other basis vectors is a hyperplane excluding it.
