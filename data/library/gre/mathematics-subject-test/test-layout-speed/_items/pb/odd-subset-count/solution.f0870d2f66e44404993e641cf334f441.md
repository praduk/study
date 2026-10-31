**Answer: C, $128$.**

**Pattern cue.** Pair symmetric terms before calculating.

**Fast route.** Fix one element. Toggling whether it belongs to a subset pairs every even-sized subset with exactly one odd-sized subset. Thus half of the $2^8$ subsets have odd size: $128$. As a check, $\binom81+\binom83+\binom85+\binom87=8+56+56+8$.

**Trap check.** The pairing needs a distinguished element; an empty ground set has no odd-sized subsets.

Review @gre:mathematics-subject-test:test-layout-speed:rk:symmetry-pairing-pattern.
