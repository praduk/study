# Physics for mathematicians

Completed 2026-09-07. A new top-level **Physics** folder is positioned immediately after Mathematics. Its eleven courses assume familiarity with the existing Mathematics curriculum, including the graduate Algebra, Analysis, Topology, and Differential Geometry material.

## Course inventory

Counts include the course guide in each subject. The Physics Course Map is one additional entry. Derivations and worked solutions are supplements, not additional entries.

| Course | Entries | Complete derivations | Worked solutions |
| --- | ---: | ---: | ---: |
| Physical Models and Conventions | 25 | 4 | 6 |
| Classical Mechanics | 38 | 18 | 7 |
| Waves and Optics | 38 | 15 | 7 |
| Electromagnetism | 35 | 11 | 7 |
| Thermodynamics | 36 | 14 | 7 |
| Statistical Mechanics | 36 | 12 | 8 |
| Special Relativity | 35 | 12 | 8 |
| Quantum Mechanics | 43 | 17 | 8 |
| Continuum Mechanics | 37 | 15 | 8 |
| General Relativity | 36 | 10 | 8 |
| Classical and Quantum Field Theory | 38 | 10 | 7 |

Total: 398 new entries, 138 theorem proof supplements, 81 solved problems, and 84 new folders including Physics and its course/topic folders. Every theorem has a main proof and every problem has a main solution. All new content is excluded from review.

## Scope and conventions

The curriculum connects mathematical structures to physical states, observables, preparations, dimensions, and approximation regimes. Empirical laws and physical-model assumptions are explicitly distinguished from conditional mathematical consequences. Each course has a guide, prerequisites, source links, definitions, derivations, and worked examples. The course map gives a reading route through the branches.

SI is the default. Relativity uses signature (-+++); electromagnetic and curvature conventions are stated explicitly. Natural units are declared locally in field theory. Thermodynamic heat into the system and work done by it are positive. Quantum inner products are conjugate-linear in the first argument. Global macros were not changed.

These are substantial course cores, not exhaustive treatments of every physics specialty. Particle, atomic, cosmological, and collective ideas appear in their appropriate courses; specialized experimental methods, plasma physics, detailed nuclear structure, advanced condensed matter, and quantum gravity are not complete courses here. Formal perturbative and continuum quantum-field expressions are labeled; no interacting four-dimensional QFT construction or global Navier–Stokes regularity theorem is claimed.

## Verification and corrections

- Independent mathematical audits checked the new proofs, worked solutions, physical assumptions, dimensions, boundary conditions, and sign conventions across all eleven courses. Corrections included normalization of the stationary probability in the detailed-balance entropy result, finite-dimensional Fock-space wording, the distinction between basis states and arbitrary states, the meaning of a Fourier-kernel comparison, an exercise's sample-count condition, the mechanical constraint associated with thermal heat capacity, a nonzero variational trial space, measurable bounded scattering potentials, and the eigenvectors required for full diagonalization of a two-level Hamiltonian.
- Source links identify inspected author or university notes and institutional references. The explanations and worked arguments were independently authored. The source conventions were checked before converting their signs or units.
- `python study.py --check-data` passes for the final v2 library: 226 folders and 1371 entries. Study validates identifiers, paths, assets, folder structure, unique tags, main variants, and supplement compatibility.
- 643 distinct reference/context checks pass using the actual Markdown parser and Study resolver. All 550 pre-existing reference checks retain their original target variant IDs. No new reference-like text remains unparsed. A punctuation issue in the Physics Course Map was corrected so each course guide is an actual reader link.
- All 398 new entries were loaded in the actual reader in both themes, including their supplements. No MathJax errors or overflowing Markdown containers were found. Content hashes tie the results to the final stored text.
- Representative 390-pixel phone reading was visually checked in both themes, including the course map, canonical mechanics, thermodynamic responses, and the Dirac derivation. The viewport remains contained and authoring controls are hidden; long equations can use contained math scrolling.
- An 18-page sample exported through Study includes a theorem with proof and a solved problem from each course in authored order. Every page was rendered and visually checked, with close-up checks of small labels after full-page previews appeared to omit text; the labels and the source PDF were intact. No text escaped page bounds and no malformed MathJax expressions remained. The current exporter displays canonical @references as literal text; the web reader resolves them normally.
- Original authored-file hashes are unchanged, including the entire Mathematics population and earlier working-tree changes. Review state/history, macros, assets, and application code were preserved. No grades or review attempts were created.
- `git diff --check` passes. No commit, push, pull, deletion of user content, or application-code change was made. Code test suites were not rerun because the task changes authored content only.

## Storage and changed paths

Physics and its empty course folders, the course map, and the foundations/field-theory entries were created through the running API. For the remaining courses, repeated whole-library writes were slow, so Study's normal `LibraryStore` methods created records in isolated per-course data copies. Those methods generated all IDs, main variants, and review modes. A combined candidate containing all existing content was validated before complete new directories were added without replacing existing paths. Subsequent corrections used the normal API, preserving IDs.

All new course content is under `data/library/physics/`. Additional artifacts are this report, [the exact changed-path list](physics-population-files.txt), and `data/exports/physics-course-sample.pdf`. No pre-existing authored file changed during this Physics task.
