# Study learning-science source ledger

**Evidence review date:** 2026-09-04

**Scope:** actionable design claims for Study's mathematics review workflow

**Method:** targeted evidence synthesis, not a registered systematic review

This is the provenance record behind `docs/LEARNING_SCIENCE.md`. Priority was given to
meta-analyses, systematic reviews, preregistered field experiments, and authoritative peer-reviewed
reviews. Exact effect estimates below are the authors' reported standardized effects; they are not
all on interchangeable scales. No estimate is treated as a guaranteed effect for one Study user.

Confidence labels rate the actionable product claim after considering relevance, amount of evidence,
heterogeneity, and domain transfer. “Remaining gap” states what Study would still need to know.

## P1 — Distribute mathematics practice over time

- **Claim:** Study should return material across separate days rather than treat massed repetition
  as equivalent practice.
- **Evidence summary:** A 2025 mathematics meta-analysis found spaced practice better than massed
  practice, `g = 0.28`, across 27 studies and 53 effects. Isolated learning produced a larger but less
  robust estimate (`g = 0.43`) than course-embedded learning (`g = 0.24`). A broader synthesis found
  839 spacing assessments in 317 experiments from 184 articles and concluded that the best interstudy
  interval grows with the target retention interval.
- **Sources:** *A Meta-analytic Review of the Effectiveness of Spacing and Retrieval Practice for
  Mathematics Learning* — Ewan Murray, Aidan J. Horner, and Silke M. Göbel; Springer Nature,
  2025; [DOI](https://doi.org/10.1007/s10648-025-10035-1). *Distributed Practice in Verbal Recall
  Tasks: A Review and Quantitative Synthesis* — Nicholas J. Cepeda, Harold Pashler, Edward Vul,
  John T. Wixted, and Doug Rohrer; American Psychological Association, 2006;
  [DOI](https://doi.org/10.1037/0033-2909.132.3.354).
- **Confidence:** High for spacing as a broad design choice; low for any particular Study interval.
- **Contradictions/limits:** Effects are heterogeneous and smaller in authentic course contexts.
  Much of the broader literature uses verbal material, not advanced proof or problem solving.
- **Remaining gap:** Which intervals best serve different mathematical content types and retention
  horizons for this learner.

## P2 — Do not present one universal “optimal” lag

- **Claim:** Scheduling must be adjustable and its constants must be disclosed as heuristic.
- **Evidence summary:** In a study of more than 1,350 people with gaps up to 3.5 months and final tests
  up to one year later, performance followed an inverted-U relation with gap. The best gap increased
  with test delay, while the best gap as a proportion of delay declined from roughly 20–40% for a
  one-week horizon to roughly 5–10% for a one-year horizon.
- **Source:** *Spacing Effects in Learning: A Temporal Ridgeline of Optimal Retention* — Nicholas J.
  Cepeda, Edward Vul, Doug Rohrer, John T. Wixted, and Harold Pashler; Association for Psychological
  Science/SAGE, 2008; [DOI](https://doi.org/10.1111/j.1467-9280.2008.02209.x).
- **Confidence:** High that useful lag depends on the desired retention interval; Low that the
  reported proportions directly prescribe a Study schedule.
- **Contradictions/limits:** Facts learned online are not the same as multi-step mathematics. A single
  review and final test do not validate a lifelong adaptive algorithm.
- **Remaining gap:** A user-selected target horizon and externally validated recall/transfer outcome.

## P3 — Require an attempt before answer exposure, with a math-specific caveat

- **Claim:** Retrieval-first review is justified, but Study must not claim a settled
  retrieval-over-restudy advantage for mathematics.
- **Evidence summary:** A classroom meta-analysis integrated 222 independent studies and 48,478
  students and reported an overall quizzing benefit of `g = 0.499`; the magnitude varied with control
  activity, feedback, test format, repetition, and design. In the 2025 mathematics review, only seven
  studies (32 effects) directly compared retrieval with restudy. Their weighted mean was `g = 0.18`,
  but the 95% confidence interval crossed zero.
- **Sources:** *Testing (Quizzing) Boosts Classroom Learning: A Systematic and Meta-Analytic Review*
  — Chunliang Yang, Liang Luo, Miguel A. Vadillo, Rongjun Yu, and David R. Shanks; American
  Psychological Association, 2021; [DOI](https://doi.org/10.1037/bul0000309). Murray, Horner, and
  Göbel, 2025; [DOI](https://doi.org/10.1007/s10648-025-10035-1). *The Effect of Testing Versus
  Restudy on Retention: A Meta-Analytic Review of the Testing Effect* — Christopher A. Rowland;
  American Psychological Association, 2014; [DOI](https://doi.org/10.1037/a0037559).
- **Confidence:** High for a general retrieval benefit; Low-to-moderate for a consistent direct
  advantage in mathematics.
- **Contradictions/limits:** The math estimate is underpowered and inconclusive, not evidence of no
  effect. General classroom results aggregate different subjects, outcomes, and control conditions.
- **Remaining gap:** More adequately powered delayed tests of mathematical statements, proof plans,
  procedures, and transfer against strong restudy/elaboration controls.

## P4 — Prefer overt retrieval but retain think-only review

- **Claim:** Written attempts should be the default, while covert retrieval remains available.
- **Evidence summary:** A 2025 meta-analysis combined 18 studies with 2,560 participants. Covert
  retrieval improved learning over no retrieval by `g = 0.23`; overt retrieval exceeded covert by
  `g = 0.17`. Covert effects depended on task form: active answer thinking and delayed judgments were
  beneficial, while answer monitoring was not reliably beneficial.
- **Source:** *Is Covert Retrieval an Effective Learning Strategy? Is It as Effective as Overt
  Retrieval? Answers from a Meta-Analytic Review* — Yadi Yu, Wenbo Zhao, Anran Li, David R. Shanks,
  Xiao Hu, Liang Luo, and Chunliang Yang; Springer Nature, 2025;
  [DOI](https://doi.org/10.1007/s10648-025-10024-4).
- **Confidence:** Moderate.
- **Contradictions/limits:** Average differences are small; materials and settings vary, and written
  production can add motor/verbal demands unrelated to mathematical understanding.
- **Remaining gap:** Whether overt proof plans and solutions improve delayed performance enough to
  justify their additional friction on a phone.

## P5 — Pair retrieval with corrective, explanatory feedback

- **Claim:** After an attempt, Study should reveal a verified canonical answer and direct comparison
  to logic, strategy, and missing dependencies—not only a correctness label.
- **Evidence summary:** A meta-analysis of 40 computer-based learning studies (70 effects) reported
  larger effects for elaborated feedback (`0.49`) than correct-answer feedback (`0.32`) or correctness
  alone (`0.05`). Experiments also found that feedback reduced later intrusion of multiple-choice
  lures and improved retention of correct answers initially given with low confidence.
- **Sources:** *Effects of Feedback in a Computer-Based Learning Environment on Students' Learning
  Outcomes: A Meta-Analysis* — Fabienne M. Van der Kleij, Remco C. W. Feskens, and Theo J. H. M.
  Eggen; American Educational Research Association, 2015;
  [DOI](https://doi.org/10.3102/0034654314564881). *Feedback Enhances the Positive Effects and Reduces
  the Negative Effects of Multiple-Choice Testing* — Andrew C. Butler and Henry L. Roediger;
  Psychonomic Society/Springer, 2008; [DOI](https://doi.org/10.3758/MC.36.3.604). *Correcting a
  Metacognitive Error: Feedback Increases Retention of Low-Confidence Correct Responses* — Andrew C.
  Butler, Jeffrey D. Karpicke, and Henry L. Roediger; American Psychological Association, 2008;
  [DOI](https://doi.org/10.1037/0278-7393.34.4.918).
- **Confidence:** Moderate-to-high.
- **Contradictions/limits:** The meta-analysis concerns item-based computer feedback across domains,
  not self-graded proofs. Feedback timing effects are not universal. A wrong canonical answer may
  reinforce error.
- **Remaining gap:** Which feedback components improve delayed proof and problem-solving outcomes,
  and whether user-authored canonical answers are sufficiently reliable.

## P6 — Use confidence for calibration, not as truth

- **Claim:** Ask for confidence after retrieval and before feedback, flag high-confidence failures,
  and avoid letting confidence dominate scheduling.
- **Evidence summary:** A meta-analysis of judgments of learning found delayed judgments more
  accurate than immediate post-study judgments. Three preregistered experiments found retrospective
  confidence more predictive of later performance in the first experiment, but the advantage was
  much smaller in the next two; their mini meta-analysis suggested only a small advantage. A review
  found that metacognitive ratings can themselves change performance, with direction and magnitude
  varying by person and task.
- **Sources:** *The Influence of Delaying Judgments of Learning on Metacognitive Accuracy: A
  Meta-Analytic Review* — Matthew G. Rhodes and Sarah K. Tauber; American Psychological Association,
  2011; [DOI](https://doi.org/10.1037/a0021705). *Confidence Ratings Are Better Predictors of Future
  Performance Than Delayed Judgments of Learning* — Adam L. Putnam, Will Deng, and K. Andrew DeSoto;
  Taylor & Francis, 2022; [DOI](https://doi.org/10.1080/09658211.2022.2026973). *Reactivity to
  Measures of Metacognition* — Kit S. Double and Damian P. Birney; Frontiers, 2019;
  [DOI](https://doi.org/10.3389/fpsyg.2019.02755).
- **Confidence:** Moderate for diagnostic value; Low that collecting confidence itself improves
  mathematical learning.
- **Contradictions/limits:** Confidence can reflect fluency, anxiety, or self-belief rather than
  correctness. Ratings are reactive, and evidence is not specific to Study's three-point scale.
- **Remaining gap:** Calibration against independently scored delayed mathematics outcomes.

## P7 — Relearn successfully in later sessions, without hard-coding a magic count

- **Claim:** Study should bring material back after successful retrieval and should distinguish later
  relearning from same-session overlearning.
- **Evidence summary:** Successive relearning means reaching a retrieval criterion in multiple spaced
  sessions. In one experiment, one correct recall in each of three spaced sessions yielded 68%
  one-week retention versus 26% after three correct recalls in one session. Two experiments reported
  large successive-relearning effects (`d = 1.52` to `4.19`) under their specific conditions.
- **Sources:** *Successive Relearning: An Underexplored but Potent Technique for Obtaining and
  Maintaining Knowledge* — Katherine A. Rawson and John Dunlosky; Association for Psychological
  Science/SAGE, 2022; [DOI](https://doi.org/10.1177/09637214221100484). *Investigating and Explaining
  the Effects of Successive Relearning on Long-Term Retention* — Katherine A. Rawson, Kalif E.
  Vaughn, Matthew Walsh, and John Dunlosky; American Psychological Association, 2018;
  [DOI](https://doi.org/10.1037/xap0000146).
- **Confidence:** Moderate for the principle; Low for Study's exact retry/interval implementation.
- **Contradictions/limits:** The research base is relatively small and homogeneous, effect estimates
  come from controlled criteria, and evidence for advanced mathematics is meager.
- **Remaining gap:** Objective mastery criteria and the number/timing of successful mathematical
  relearning sessions needed for durable performance.

## P8 — Use authored order for deliberate, not automatic, interleaving

- **Claim:** Preserve author control of order and encourage intentional alternation among confusable
  mathematical strategies; do not randomly mix everything.
- **Evidence summary:** A preregistered cluster-randomized trial across 54 seventh-grade classes used
  four months of practice and an unannounced test one month later; interleaved classes scored 61%
  versus 38% for blocked classes (`d = 0.83`). A meta-analysis of 59 studies and 238 effects found a
  positive mathematics estimate (`g = 0.34`, 95% CI `[0.11, 0.57]`) with high heterogeneity, while
  word learning favored blocking (`g = -0.39`). A systematic review concludes that similarity and
  category structure determine whether interleaving supports discrimination.
- **Sources:** *A Randomized Controlled Trial of Interleaved Mathematics Practice* — Doug Rohrer,
  Robert F. Dedrick, Marissa K. Hartwig, and Chi-Ngai Cheung; American Psychological Association,
  2020; [DOI](https://doi.org/10.1037/edu0000367). *Similarity Matters: A Meta-Analysis of Interleaved
  Learning and Its Moderators* — Matthias Brunmair and Tobias Richter; American Psychological
  Association, 2019; [DOI](https://doi.org/10.1037/bul0000209). *A Systematic Review of Interleaving
  as a Concept Learning Strategy* — Jonathan Firth, Ian Rivers, and James Boyle; Wiley, 2021;
  [DOI](https://doi.org/10.1002/rev3.3266).
- **Confidence:** Moderate.
- **Contradictions/limits:** The large field result concerns school mathematics and a particular
  worksheet design. Meta-analytic heterogeneity is substantial; internally diverse categories may
  initially benefit from blocking.
- **Remaining gap:** A validated rule for when two Study entries are confusable enough to interleave,
  and whether contiguous modes per entry help or hinder discrimination.

## P9 — Provide worked solutions for novices and fade support with expertise

- **Claim:** Verified worked solutions are appropriate feedback for novice learners, but assistance
  should not remain fixed as expertise grows.
- **Evidence summary:** A mathematics meta-analysis found an average worked-example effect of
  `g = 0.48` (`p = .01`) across 43 articles, 55 studies, and 181 effects. Correct examples alone were
  more beneficial than incorrect-only or mixed correct/incorrect examples; adding self-explanation
  prompts was a negative moderator. An expertise-reversal meta-analysis of 176 effects from 60
  studies found high assistance benefited low-prior-knowledge learners (`d = 0.505`, 95% CI
  `[0.260, 0.750]`) but harmed high-prior-knowledge learners relative to low assistance
  (`d = -0.428`, 95% CI `[-0.647, -0.209]`), with high heterogeneity.
- **Sources:** *A Meta-Analysis of the Worked Examples Effect on Mathematics Performance* — Christina
  Areizaga Barbieri, Dana Miller-Cotto, Sarah N. Clerjuste, and Kamal Chawla; Springer Nature, 2023;
  [DOI](https://doi.org/10.1007/s10648-023-09745-1). *A Cornerstone of Adaptivity—A Meta-Analysis of
  the Expertise Reversal Effect* — Leonard Tetzlaff, Bianca Simonsmeier, Tabea Peters, and Garvin
  Brod; Elsevier, 2025; [DOI](https://doi.org/10.1016/j.learninstruc.2025.102142).
- **Confidence:** Moderate-to-high for worked examples and prior-knowledge-sensitive assistance;
  Low for any automatic fading rule in Study.
- **Contradictions/limits:** Moderator categories are broad and heterogeneous. The negative
  self-explanation moderator conflicts with the positive average self-explanation literature,
  showing that combining individually useful features can fail.
- **Remaining gap:** A reliable, low-burden estimate of topic-specific prior knowledge and a tested
  fading policy for proof/problem support.

## P10 — Prompt generation and self-explanation selectively

- **Claim:** Ask learners to generate examples, reasons, and solution plans, but do not attach a
  generic “explain” prompt to every item.
- **Evidence summary:** A generation-effect meta-analysis combined 445 effects from 86 studies and
  reported a positive average effect of about `0.40` with substantial moderation. A general
  self-explanation meta-analysis across 69 effects from 64 reports found `g = 0.55`. A mathematics
  meta-analysis found immediate effects of `0.28` for procedures, `0.33` for concepts, and `0.46` for
  transfer. Only nine experiments included a delayed test: transfer remained positive (`0.32`),
  while procedural (`0.13`) and conceptual (`-0.05`) estimates were nonsignificant.
- **Sources:** *The Generation Effect: A Meta-Analytic Review* — Sharon Bertsch, Bryan J. Pesta,
  Richard Wiscott, and Michael A. McDaniel; Psychonomic Society/Springer, 2007;
  [DOI](https://doi.org/10.3758/BF03193441). *Inducing Self-Explanation: A Meta-Analysis* — Kiran
  Bisra, Qing Liu, John C. Nesbit, Farimah Salimi, and Philip H. Winne; Springer Nature, 2018;
  [DOI](https://doi.org/10.1007/s10648-018-9434-x). *Promoting Self-Explanation to Improve Mathematics
  Learning: A Meta-Analysis and Instructional Design Principles* — Bethany Rittle-Johnson, Abbey M.
  Loehr, and Kelley Durkin; Springer Nature, 2017;
  [DOI](https://doi.org/10.1007/s11858-017-0834-z).
- **Confidence:** Moderate for targeted prompts; Low for durable gains from generic prompting.
- **Contradictions/limits:** Effects depend on prompts, materials, and control tasks. Classroom and
  delayed mathematics evidence is limited; worked-example research found a negative prompt moderator.
- **Remaining gap:** Which prompt forms yield correct mathematical explanations without displacing
  attention from the proof or procedure itself.

## P11 — Measure transfer separately and honestly

- **Claim:** Routine statement, proof, and solution reviews must not be presented as evidence of
  broad transfer. Transfer should be evaluated separately with unseen applications when needed.
- **Evidence summary:** A meta-analysis covered 192 transfer effects from 122 experiments, 67 reports,
  and 10,382 participants. Retrieval practice had an overall transfer estimate of `d = 0.40` (95% CI
  `[0.31, 0.50]`) against non-testing re-exposure. Transfer was stronger across test formats and for
  application/inference tasks, and weaker for several forms including unpracticed material and
  worked-example problems; practice elaboration and initial success moderated outcomes.
- **Source:** *Transfer of Test-Enhanced Learning: Meta-Analytic Review and Synthesis* — Steven C. Pan
  and Timothy C. Rickard; American Psychological Association, 2018;
  [DOI](https://doi.org/10.1037/bul0000151).
- **Confidence:** Moderate that transfer can occur; Low that a generic self-graded prompt would
  measure far transfer.
- **Contradictions/limits:** Categories aggregate diverse tasks and publication-bias adjustments
  weaken some estimates. Most studies are not advanced mathematics.
- **Remaining gap:** Independently scored, unseen problems at a meaningful delay and a predefined
  notion of near versus far mathematical transfer.

## P12 — Do not optimize for immediate ease or arbitrary struggle

- **Claim:** Study should separate current performance from durable learning and avoid a universal
  target failure rate.
- **Evidence summary:** A major review documents that conditions improving performance during
  practice can impair long-term learning and vice versa. Experimental work on high-element-
  interactivity material shows that added difficulty and depleted working-memory resources can turn
  an intended “desirable difficulty” into an undesirable one.
- **Sources:** *Learning Versus Performance: An Integrative Review* — Nicholas C. Soderstrom and
  Robert A. Bjork; Association for Psychological Science/SAGE, 2015;
  [DOI](https://doi.org/10.1177/1745691615569000). *Undesirable Difficulty Effects in the Learning of
  High-Element Interactivity Materials* — Ouhao Chen, Juan C. Castro-Alonso, Fred Paas, and John
  Sweller; Frontiers, 2018; [DOI](https://doi.org/10.3389/fpsyg.2018.01483).
- **Confidence:** Moderate as a guardrail; Low for a numeric difficulty target.
- **Contradictions/limits:** “Desirable difficulty” names a conditional outcome, not a manipulable
  dose. Cognitive load and prior knowledge are difficult to infer from Study interaction data.
- **Remaining gap:** Behavioral criteria distinguishing productive retrieval difficulty from an
  underspecified, overloaded, or inaccessible task.

## P13 — Treat sleep as a learning boundary, not a software signal

- **Claim:** Study should not glorify sleep-depriving study or infer sleep-stage-aware scheduling
  from review data.
- **Evidence summary:** Meta-analyses of total sleep deprivation found impairment when deprivation
  occurred before learning (`g = 0.621`, 95% CI `[0.473, 0.769]`) and after learning (`g = 0.277`,
  95% CI `[0.177, 0.377]`). A later synthesis of 39 reports, 125 effects, and 1,234 participants found
  that restricting sleep to 3–6.5 hours versus 7–11 hours impaired memory formation by `g = 0.29`
  (95% CI `[0.13, 0.44]`).
- **Sources:** *Sleep Deprivation and Memory: Meta-Analytic Reviews of Studies on Sleep Deprivation
  Before and After Learning* — Chloe R. Newbury, Rebecca Crowley, Kathleen Rastle, and Jakke
  Tamminen; American Psychological Association, 2021;
  [DOI](https://doi.org/10.1037/bul0000348). *A Systematic and Meta-Analytic Review of the Impact of
  Sleep Restriction on Memory Formation* — Rebecca Crowley, Eleanor Alderman, Amir-Homayoun Javadi,
  and Jakke Tamminen; Elsevier, 2024; [DOI](https://doi.org/10.1016/j.neubiorev.2024.105929).
- **Confidence:** High that sleep loss impairs memory on average; Low for a software scheduling rule.
- **Contradictions/limits:** Studies vary in sleep manipulation, timing, memory system, and recovery.
  These findings do not establish a personalized bedtime, diagnose sleep, or identify an optimal
  review time.
- **Remaining gap:** None required for the current guardrail. Any sleep-sensitive feature would need
  new consent, privacy, clinical-safety, and validation work.

## P14 — Personalization is plausible, but Study's formula is not validated personalization

- **Claim:** Preserve per-card history and expose the algorithm, but call the present update rule a
  heuristic until it predicts delayed outcomes.
- **Evidence summary:** A personalized scheduler for foreign-language learning improved retention by
  16.5% over massed practice and 10% over a generic spaced schedule in a semester-long deployment.
  This demonstrates that adaptive schedules can beat fixed alternatives in one domain; it does not
  validate Study's stability/difficulty formula.
- **Source:** *Improving Students' Long-Term Knowledge Retention Through Personalized Review* —
  Robert V. Lindsey, Jeffery D. Shroyer, Harold Pashler, and Michael C. Mozer; Association for
  Psychological Science/SAGE, 2014; [DOI](https://doi.org/10.1177/0956797613504302).
- **Confidence:** Moderate that validated personalization can help; Low for transfer to mathematics
  or to Study's present scheduler.
- **Contradictions/limits:** The target was foreign-language vocabulary, the model and outcomes
  differ from Study, and percentages are relative deployment results rather than universal gains.
- **Remaining gap:** Prospective calibration of predicted recall and transfer, comparison with a
  fixed spaced baseline, and validation by mathematical content type.

## P15 — Fit forgetting predictions, but calibrate them only to the observed target

- **Claim:** Study may use delayed review history to fit a transparent forgetting curve to the
  learner's probability of self-grading Good or Easy, provided the app does not relabel that target
  as objective recall, correctness, or mastery.
- **Evidence summary:** Half-life regression combined an explicit exponential forgetting curve with
  trainable parameters and improved recall prediction over several baselines on large-scale
  language-learning data. A separate longitudinal memory experiment found that an exponential curve
  fit individual data well while Bayesian model comparison favored a power function, demonstrating
  that plausible forgetting-curve forms can imitate one another. These results support fitting and
  comparing explicit predictive models; they do not validate Study's curve, prior, threshold, or
  safety bounds.
- **Sources:** *A Trainable Spaced Repetition Model for Language Learning* — Burr Settles and Brendan
  Meeder; Association for Computational Linguistics, 2016;
  [DOI](https://doi.org/10.18653/v1/P16-1174). *The Form of the Forgetting Curve and the Fate of
  Memories* — Lee Averell and Andrew Heathcote; Elsevier, 2011;
  [DOI](https://doi.org/10.1016/j.jmp.2010.08.009).
- **Confidence:** Moderate that delayed outcomes can train an explicit forgetting model; Low for
  Study's exact discounted Bayesian implementation and its transfer to mathematical review.
- **Contradictions/limits:** The trainable deployment concerned language items, not theorem proofs
  or problem solving. Study observes self-grades, its cards vary substantially in scope, and a good
  retrospective fit can still be poorly calibrated prospectively. The exponential curve is an
  engineering choice rather than an established universal law.
- **Remaining gap:** Chronological calibration results for this learner, adequate observations by
  task mode, comparison with the prior fixed scheduler, and separately scored mathematical outcomes
  if claims beyond self-grading behavior are ever desired.

## Evidence-to-feature audit

| Current Study behavior | Ledger support | Honest status |
| --- | --- | --- |
| Due dates and expanding successful intervals | P1, P2 | Broadly supported mechanism; exact constants unvalidated |
| Attempt required before reveal | P3, P4 | Strong general rationale; math-specific comparative evidence inconclusive |
| Canonical answer plus comparison cues | P5 | Supported, conditional on answer correctness |
| Confidence before reveal | P6 | Calibration instrumentation; not a mastery signal |
| Again retry after up to three available cards and ten-minute due time | P7 | Engineering approximation; not a validated criterion schedule |
| Authored-order queue | P8 | Enables deliberate sequencing; not automatic interleaving |
| Matching statement, proof, or solution revealed after attempt | P5, P9 | Useful feedback/novice support; no automatic fading |
| Fixed kind-specific define/state, theorem-proof, and problem-solve tasks | P3, P5, P11 | Clear retrieval targets; exact prompt verbs are product copy, and repeated success does not establish transfer |
| Optional written response on larger screens; fixed think-only review on phones | P4 | Overt retrieval has a small average advantage; the device rule is a usability choice, not an evidence-derived breakpoint |
| No streak or universal target failure rate | P12 | Appropriate guardrail |
| No sleep-derived scheduling | P13 | Appropriate evidentiary and privacy boundary |
| Bayesian interval fitting to delayed Good/Easy self-grades | P14, P15 | Transparent personalized prediction; prospective calibration unestablished and not an objective mastery measure |

## Research maintenance rules

- Recheck this ledger before changing review claims or algorithms.
- Add a provenance record for every new actionable learning-science claim.
- Prefer a direct DOI/publisher link and report sample/effect details exactly.
- Record nulls, crossed confidence intervals, heterogeneity, and domain mismatch—not only favorable
  estimates.
- Do not cite the same broad effect as validation of an exact UI or interval constant.
- Mark preregistration, field setting, objective scoring, and delayed outcomes when they materially
  change confidence.
- Treat future Study telemetry as observational until a prospective comparison supports a causal
  claim.
