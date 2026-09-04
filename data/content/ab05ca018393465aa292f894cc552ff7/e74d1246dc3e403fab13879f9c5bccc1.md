The integers are enumerated by
$0,1,-1,2,-2,\ldots$, giving an explicit bijection with $\omega$.

Every rational is represented by a pair $(p,q)\in\mathbb Z\times(\omega\setminus\{0\})$. Since both factors have explicit enumerations, their product is countable. Enumerate the pairs and list the value $p/q$ at each stage. For each rational choose the least stage at which it appears; this injects $\mathbb Q$ into $\omega$.

For strings, first obtain an enumeration from the stated countability assumption. Let $j:A\to\omega$ be injective and fix one $a_0\in A$, possible because $A$ is nonempty. Define $e:\omega\to A$ by letting $e(m)$ be the unique $a\in A$ with $j(a)=m$ when such an $a$ exists, and putting $e(m)=a_0$ otherwise. Then $e$ is surjective. (This fixes only one witness and does not use the Axiom of Choice.)

Now $A^{<\omega}=\bigcup_{n\in\omega}A^n$. The set $A^0$ is the singleton containing the empty function, so use the constant enumeration at that function. For $n>0$, apply $e$ coordinatewise to an explicit enumeration of $\omega^n$; this gives a surjection $\omega\to A^n$, uniformly in $n$. The preceding enumerated-union theorem therefore makes $A^{<\omega}$ countable. A nonempty finite alphabet is covered because every finite set injects into $\omega$.
