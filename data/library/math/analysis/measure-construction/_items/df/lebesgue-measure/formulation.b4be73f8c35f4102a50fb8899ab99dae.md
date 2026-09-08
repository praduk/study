Lebesgue @[outer measure]math:analysis:measure-construction:df:outer-measure on $\R$ is

$$
m^*(E)=\inf\left\{\sum_{n=1}^{\infty}|I_n|:E\subseteq\bigcup_n I_n,\ I_n\text{ open intervals}\right\},
$$

where $|I_n|$ denotes interval length. Lebesgue measurable sets are the Carathéodory measurable sets for this outer measure, and Lebesgue measure is its restriction. This is the completion of the Borel measure determined by interval lengths. The construction and interval-length identification are established in Hunter, [Measure Theory, Chapter 2](https://www.math.ucdavis.edu/~hunter/measure_theory/measure_notes.pdf).

Every singleton is null: cover it by intervals of arbitrarily small length. Countable subadditivity then makes every countable subset null. Borel and Lebesgue measurability are different notions; completion adds every subset of every Borel null set.
