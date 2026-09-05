# Learning science in Study

Study is designed to make durable mathematical learning more likely. It cannot certify that a
theorem is understood, a proof is valid, or a skill will transfer. The strongest relevant evidence
supports distributing practice over time. Evidence for retrieval practice is broad and substantial
in general education, but the direct mathematics-specific comparison with restudy is presently
small and inconclusive. Product language and decisions must preserve that distinction.

This document describes the implemented behavior and the reasoning behind it. The auditable source
ledger is in [`research/report-source.md`](research/report-source.md). The evidence was last reviewed
on 2026-09-04.

## Evidence posture

Study uses three confidence levels:

- **High:** replicated evidence or a directly relevant meta-analysis supports the broad intervention.
- **Moderate:** evidence is useful but indirect, heterogeneous, or dependent on learner/task design.
- **Low:** a plausible product heuristic has not been validated for this application.

The levels describe confidence in a product claim, not a quality score for a paper.

| Design commitment | Evidence confidence | What Study may honestly claim |
| --- | --- | --- |
| Space encounters across days | High | Spaced practice improves delayed mathematics performance on average, though effects are not uniform. |
| Attempt retrieval before revealing | High in general education; low-to-moderate for mathematics specifically | Retrieval is a defensible practice mechanism, but a math-specific advantage over restudy is not established. |
| Show corrective, explanatory feedback | Moderate-to-high | Feedback is generally more useful when it supplies the answer and explanation rather than correctness alone. |
| Prefer an overt answer while allowing think-only review | Moderate | Covert retrieval can help, but overt retrieval has a small average advantage and is easier to audit. |
| Record confidence after an attempt | Moderate as a diagnostic; low as a causal intervention | Confidence can expose calibration errors; it is not proof of knowledge. |
| Mix deliberately chosen confusable problem types | Moderate | Mathematics interleaving can improve delayed discrimination, but arbitrary mixing can be harmful. |
| Give novices worked solutions, then fade support | Moderate-to-high | Worked examples help mathematics on average; the right amount of assistance depends on prior knowledge. |
| Prompt explanation and transfer | Moderate | These prompts can deepen learning, but delayed and classroom mathematics evidence is less secure. |
| Self-calibrate intervals to delayed self-grades | Low | Study fits a transparent Bayesian forgetting model to the learner's own grading behavior; this predicts self-grades, not objective mastery. |

## The exact review flow

A review card is the pair `<entry-id>::<mode>`. Alternative formulations, proofs, and solutions do
not receive independent cards. They are feedback attached to the entry-mode card.

Starting Review loads an in-memory batch of at most 200 cards. A card is included when it has no
`due_at` timestamp or when `due_at` is at or before the current UTC time. After the batch is exhausted,
Study requests the next due batch and only reports completion after a fresh request is empty. A card
that becomes due during a long session can therefore join a later batch. An Again retry is also
inserted after up to three currently available intervening cards in the in-memory batch.

For each card, Study does the following:

1. Shows the canonical tag, title, custom header, mode, and kind-specific prompt. `solve` and
   `proof-plan` also show the main formulation as the prompt body, so the problem or theorem
   statement is available.
2. Requests an attempt. Larger screens provide an optional written response; an empty response is
   recorded as think-only. Phone layouts are always think-only and do not show a text field. Study
   does not currently provide hints.
3. Requires a retrospective confidence rating—Unsure (`1`), Somewhat (`2`), or Confident (`3`)—after
   the attempt and before answer exposure. The browser submits attempt, confidence, elapsed time,
   overt/covert status together.
4. Reveals only the answer family for the active task and its alternatives: formulations for a
   statement, proofs for a theorem proof task, or solutions for a problem. The written attempt is
   rendered with Markdown and MathJax for direct comparison.
5. Requests a self-grade:

   | Key | Grade | UI criterion |
   | --- | --- | --- |
   | `1` | Again (`0`) | Major gap or no valid method |
   | `2` | Hard (`1`) | Partial, slow, or needed help |
   | `3` | Good (`2`) | Correct and unaided |
   | `4` | Easy (`3`) | Fluent and precise |

6. Stores the schedule state and appends the full graded attempt to `data/review-log.jsonl`.

Study does not parse the attempt, check a proof, or infer correctness. The learner's self-grade drives
the schedule. That is a material limitation, not an implementation detail.

### Fixed review tasks

- **Definition:** “Define `<title>`.”
- **Axiom:** “State `<title>`.”
- **Remark:** state the content precisely.
- **Theorem:** “State `<title>`.” When a main proof exists, a second task says “Prove
  `<title>`.” and displays the theorem statement.
- **Problem:** “Solve the following problem.” The problem statement is displayed, and the task
  exists only when a main solution is stored.

These tasks are intentionally not configurable. The internal `proof-plan` card ID is retained for
schedule compatibility, but the prompt and visible label require a proof, not merely a plan.

## Authored-order review

Study intentionally uses authored order as curricular control. The queue traverses the library in
preorder:

1. root folders by stored `order`;
2. each folder's direct entries by stored `order`;
3. each entry's fixed tasks—statement before theorem proof;
4. then the folder's child folders recursively, each by stored `order`.

Only eligible due/new cards are emitted, so skipping a not-due card does not alter the relative order
of those that remain. Disabling a folder excludes its direct entries and all descendant folders. A
child marked enabled is still excluded while an ancestor is disabled.

Authored order is not the same as blocked practice. An author can deliberately alternate confusable
problem families or place a definition before the theorem that depends on it. Study does not
automatically identify confusability, randomize items, or optimize interleaving. That restraint is
intentional: interleaving benefits depend on category similarity and task design, and arbitrary
mixing can increase irrelevant load or even favor blocking.

One current consequence is that all due modes for an entry are adjacent. If a future change scatters
modes or dynamically interleaves entries, it must preserve a user-controlled order option and be
evaluated against delayed mathematical performance, not just session completion.

## The self-calibrating scheduling model

The scheduler retains a per-card stability estimate `S` in days and difficulty `D` on a nominal
`1`–`10` scale. A new card starts from `S = 0.5` and `D = 5.0`. The grade-specific state update is:

| Grade | New stability `S'` | New difficulty `D'` | Minimum interval | Other state |
| --- | --- | --- | --- | --- |
| Again (`0`) | `min(3650, max(0.25, 0.45 S))` | `min(10, D + 0.7)` | exactly 10 minutes | increment lapses; retry after up to three available intervening cards |
| Hard (`1`) | `min(3650, max(1, 1.35 S))` | `min(10, D + 0.2)` | 1 day | increment repetitions |
| Good (`2`) | `min(3650, max(2, S(2.25 - 0.035 D)))` | `max(1, D - 0.15)` | 1 day | increment repetitions |
| Easy (`3`) | `min(3650, max(4, S(3.1 - 0.045 D)))` | `max(1, D - 0.35)` | 2 days | increment repetitions |

Study persists stability to three decimal days after this update.

For Hard, Good, and Easy, Study multiplies `S'` by a learned interval factor before rounding to an
integer day. The learned target is the probability that the learner will self-grade the next
retrieval **Good or Easy**. Again and Hard are observations below that target; Good and Easy are
observations at or above it. The model does not infer correctness from the written attempt.

For an actual delay `t`, normalized delay `x = t / S`, and positive interval-scale parameter `c`,
the model is

$$
P(\text{Good or Easy}\mid x,c)
= \epsilon + (1-2\epsilon)\exp\!\left(-\gamma\frac{x}{c}\right),
$$

where `epsilon = 0.02`, the target `q = 0.90`, and
`gamma = -log((q-epsilon)/(1-2 epsilon))`. Thus `c = 1` predicts 90% at `t = S`, while every finite
`c` retains strictly positive forgetting. Study represents `c` with 161 logarithmically spaced
values from `1/8` through `8`. The normalized prior masses on those points form a bounded, discrete
approximation to a log-normal prior with `log(c) ~ Normal(0, 0.70^2)`, truncated to the grid. It is
not an unbounded continuous log-normal distribution.

For a repeat review, `t` runs from completion of the previous graded review to the recorded start of
the new retrieval. Qualification therefore uses retrieval start, not the later time at which the
learner submits a grade. First reviews and delays under six hours are excluded. For an eligible
review, the model input is `x* = min(t/S, 64)` and the binary outcome is `y = 1` for Good or Easy and
`0` for Again or Hard. A tab left open for six hours is not explicitly classified as an in-session
retry. The cap prevents one extremely overdue review from having unbounded leverage and is recorded
in the audit event. Reporting is stricter than the capped update: it omits a numerical forecast and
returns a status explaining why when the delay is under six hours or the uncapped normalized delay
exceeds `64`.

For grid point `c_i`, prior mass `pi_i`, current posterior mass `w_i`, and discount `delta = 0.995`,
the next posterior is the normalized discrete distribution

$$
w'_i \propto w_i^\delta\,\pi_i^{1-\delta}
P(y\mid x^*,c_i).
$$

Study applies that update to both a pooled model and the matching statement, theorem-proof, or
problem-solution model. It also updates `N_eff' = delta N_eff + 1`, successful effective weight
`K_eff' = delta K_eff + y`, and exposure `E' = delta E + min(x*, 4)`. A model becomes ready only when
all six gates hold: at least 24 raw observations, observations from at least eight distinct cards,
`N_eff >= 20`, `E >= 12`, posterior standard deviation `SD(log(c)) <= 0.65`, and strictly less than
5% posterior mass at each endpoint of the bounded grid. The distinct-card and endpoint gates guard
against one repeatedly reviewed card creating false precision and against a credible interval being
artificially narrowed by a grid boundary. They do not make repeated observations independent. A
ready task-specific posterior is preferred; otherwise Study uses a ready pooled posterior. Until
either is ready, the interval factor is exactly `1`, preserving the prior scheduler's intervals.

For scheduling, Study computes the posterior predictive probability
`p_bar(f) = sum_i w_i P(Good or Easy | x=f, c_i)`. It chooses the root `p_bar(f) = 0.90` by bisection,
bounded to `0.5 <= f <= 2.0`; if no root lies inside that range, it uses the nearer boundary. For
Hard, Good, or Easy, the integer-day interval is
`min(3650, max(grade minimum, round(S' f)))`. Again remains exactly ten minutes and does not use the
learned factor. Both retained stability and scheduled intervals are capped at 3,650 days. Reporting
includes the suggested factor, whether the 90% target is attainable inside the permitted factor
range, and whether the suggestion is boundary-limited in the shorter or longer direction. A
boundary suggestion is an operational safety limit, not a claim that the target probability was
achieved.

The `0.995` power-prior discount is applied once per qualified observation. It is observation-count
discounting, not wall-clock decay: the posterior does not change merely because days or years pass.
As new qualified observations arrive, recent grading behavior can eventually outweigh older
behavior while evidence changes gradually. Scheduling uses the posterior available before the
current grade; the current grade updates subsequent schedules. The pre-outcome probability and
full-precision normalized delay are written to the append-only review log, and the derived posterior
can be reconstructed from that log after an interrupted state write.

If a learner chooses Confident (`3`) and then grades Again, Study adds another `0.35` to difficulty,
capped at `10`. It stores a simple calibration value:

```text
calibration = confidence - expected-confidence-for-grade
expected confidence: Again=1, Hard=2, Good=2, Easy=3
```

Confidence otherwise does not affect the interval. Overt/covert status and elapsed time are logged
but do not change scheduling. Again's ten-minute due timestamp and its in-session retry are separate
behaviors: the retry is inserted after up to three available intervening cards even if ten minutes
have not elapsed.

The prior, curve, target, activation gates, discount, and safety bounds are transparent engineering
choices, not empirically optimal constants. The model treats qualified observations as conditionally
independent given `c`, even though repeated reviews of one card and results from the same learner are
correlated. The distinct-card gate is a safeguard, not a hierarchical or repeated-measures model.
Its 90% credible interval is conditional on this curve, prior, bounded grid, independence
approximation, and observed data; it is not a general guarantee about learner uncertainty.

The observed data are also selected: only reviews the learner completes can produce a self-grade.
Skipped, delayed, or selectively avoided reviews have no outcome, so the estimates are conditional
on completed reviews and may be biased by that selection. The model is fitted only to this learner's
Good-or-Easy self-grades. It must not be described as measuring objective remembering, correctness,
durable mathematical competence, mastery, or transfer.

### Read-only calendar and history reporting

`GET /api/review/calendar` reports current schedule snapshots and validated review history over a
half-open, timezone-aware interval: `start` is inclusive and `end` is exclusive. The interval is
limited to 366 days. With neither bound supplied, it starts at the current UTC day and spans 90
days; supplying only one bound creates the same 90-day span on the other side.

Each event is the one currently stored next-due time for a reviewed card, not a generated recurrence.
Active cards are derived from the current library, fixed task availability, and inherited folder
review setting. New cards have no stored schedule and are omitted. Review-disabled schedules and
orphaned schedules for deleted entries or removed tasks are omitted unless `include_inactive=true`.
The stored schedule at the last grade is returned with the current entry title, canonical tag, task
label, and active-state classification. The endpoint reconstructs state in memory from the complete
log and fails closed on malformed history; it does not write either review file.

Statistics count every validated log record completed within the interval, so repeated same-day
attempts remain distinct. They include elapsed minutes, the four self-grade counts, Again lapses,
the Good-or-Easy self-grade rate, and zero-filled daily buckets. Buckets use UTC by default; an
optional bounded `timezone` query accepts an IANA time-zone name for local calendar labels without
changing the instant-based range or totals. These history totals retain attempts for content that is
now review-disabled or deleted, consistent with the append-only log.

Bayesian reporting includes each posterior interval-scale median and equal-tail 90% credible
interval, endpoint mass, distinct-card count, readiness gates, suggested interval factor, target
attainability, and any boundary-limited direction. Per-event output identifies the scheduling source
and posterior used for forecasts. A numerical `predicted_good_or_easy_now` or
`predicted_good_or_easy_at_due` is returned only inside the reporting domain: at least six hours
since the prior completed review and an uncapped normalized delay no greater than `64`. Otherwise a
prediction status explains that the estimate was omitted. While readiness gates are unmet, the
source remains `fallback` and the task posterior is explicitly marked as collecting; those posterior
outputs are diagnostics, not calibrated scheduling inputs.

Forecast evaluation uses validated probabilities written before their outcomes were known. It
reports the eligible forecast count, mean Brier score, mean log loss, and reliability bins containing
the number of forecasts, their mean predicted probability, and their observed Good-or-Easy
self-grade rate. The aggregate includes compatible logged forecasts from earlier model versions;
legacy observations without a recorded pre-outcome probability are excluded rather than scored with
a reconstructed forecast. These are retrospective diagnostics conditional on completed reviews.
Small or selectively observed samples can be misleading, and neither a posterior credible interval
nor a good in-sample score establishes prospective calibration. Every forecast is about a future
Good-or-Easy self-grade, never objective remembering, correctness, mastery, or transfer.

## Why the design uses these practices

### Spacing: strongest direct mathematics evidence

The 2025 mathematics meta-analysis by Murray, Horner, and Göbel found a robust overall advantage of
spaced over massed practice, `g = 0.28`, across 27 studies and 53 effects. The course-embedded subset
was smaller (`g = 0.24`) than isolated learning (`g = 0.43`). This supports returning on later days,
not a particular interval multiplier. General spacing syntheses also show that the useful gap depends
on the desired retention interval; one fixed cadence cannot be optimal for every horizon.

Product implications:

- Make due dates visible and allow forgetting between successful sessions.
- Do not reward same-session repetition as if it were equivalent to relearning later.
- Keep interval constants inspectable and versioned.
- Evaluate any scheduler against delayed outcomes at more than one retention horizon.

Sources: [Murray, Horner, and Göbel (2025)](https://doi.org/10.1007/s10648-025-10035-1),
[Cepeda et al. (2006)](https://doi.org/10.1037/0033-2909.132.3.354), and
[Cepeda et al. (2008)](https://doi.org/10.1111/j.1467-9280.2008.02209.x).

### Retrieval: broad support, weaker mathematics-specific support

A large classroom meta-analysis found an average benefit of quizzing across 222 independent studies
and 48,478 students (`g = 0.499`), with important moderators including control activity, feedback,
format, repetition, and design. However, the 2025 math-specific review found only seven studies (32
effects) comparing retrieval with restudy; its weighted mean was `g = 0.18`, but the 95% confidence
interval crossed zero. The appropriate conclusion is not “retrieval does not work in mathematics.” It
is that the direct math literature is too small and inconsistent to establish a reliable average
advantage.

Study therefore requires an attempt before reveal and separates statement, theorem-proof, and
problem-solution retrieval. It does not claim that statement recall alone establishes proof or
problem-solving mastery.

Sources: [Yang et al. (2021)](https://doi.org/10.1037/bul0000309),
[Rowland (2014)](https://doi.org/10.1037/a0037559), and
[Murray, Horner, and Göbel (2025)](https://doi.org/10.1007/s10648-025-10035-1).

### Overt attempts and think-only review

A 2025 meta-analysis found a small benefit of covert retrieval over no retrieval (`g = 0.23`) across
18 studies and 2,560 participants, and a small advantage of overt over covert retrieval (`g = 0.17`).
Effects varied by how covert retrieval was elicited, feedback, material, and delay. Study offers a
written response on larger screens because it externalizes omissions and makes comparison easier,
while an empty response records think-only retrieval. Phone review is fixed to think-only as a
usability choice; the evidence does not validate that device breakpoint.

Source: [Yu et al. (2025)](https://doi.org/10.1007/s10648-025-10024-4).

### Feedback and error correction

In a meta-analysis of computer-based learning, elaborated feedback had a larger average effect
(`0.49`) than showing the correct answer (`0.32`) or correctness alone (`0.05`). Other experiments
show that feedback can correct multiple-choice lure errors and improve retention of low-confidence
correct answers. Study reveals canonical content and explicit comparison cues rather than a bare
right/wrong flag.

This is only as good as the stored answer. Incorrect canonical content can consolidate error, which
is why mathematical verification rules in `AGENTS.md` are strict.

Sources: [Van der Kleij, Feskens, and Eggen (2015)](https://doi.org/10.3102/0034654314564881),
[Butler and Roediger (2008)](https://doi.org/10.3758/MC.36.3.604), and
[Butler, Karpicke, and Roediger (2008)](https://doi.org/10.1037/0278-7393.34.4.918).

### Confidence is calibration data, not correctness

Delayed judgments of learning are generally better calibrated than immediate post-study judgments,
and retrospective confidence after retrieval may predict later performance slightly better in some
settings. The advantage was much smaller in two of three preregistered experiments, and metacognitive
ratings can themselves change performance in inconsistent directions. Study collects a coarse
post-attempt confidence rating to expose high-confidence failures and support future analysis. It
does not treat confidence as correctness or let confidence broadly control the interval.

Sources: [Rhodes and Tauber (2011)](https://doi.org/10.1037/a0021705),
[Putnam, Deng, and DeSoto (2022)](https://doi.org/10.1080/09658211.2022.2026973), and
[Double and Birney (2019)](https://doi.org/10.3389/fpsyg.2019.02755).

### Successive relearning

Successive relearning combines successful retrieval with relearning in later sessions. In one study,
one correct recall in each of three spaced sessions produced much better one-week retention than
three correct recalls in one session (68% versus 26%). Reviews describe large and promising effects,
but the literature is much smaller and more homogeneous than the broad spacing literature and offers
little direct evidence for advanced mathematics.

Study's later due dates and same-session Again retry approximate parts of this method; they do not
enforce an objective accuracy criterion or a fixed number of successful sessions. The app therefore
must not claim to implement a validated successive-relearning protocol.

Sources: [Rawson and Dunlosky (2022)](https://doi.org/10.1177/09637214221100484) and
[Rawson et al. (2018)](https://doi.org/10.1037/xap0000146).

### Interleaving and authored order

A preregistered cluster-randomized trial in 54 seventh-grade mathematics classes reported 61% versus
38% on an unannounced test one month later for interleaved versus blocked practice (`d = 0.83`). A
broader meta-analysis found a positive but heterogeneous mathematics effect; it also found a blocking
advantage in word learning. A systematic review emphasizes similarity and category structure: mixing
is useful when choosing the correct strategy among confusable categories, not as random variety.

Study leaves sequence with the author. Arrange discriminations and problem families deliberately;
do not infer that any shuffle is beneficial.

Sources: [Rohrer et al. (2020)](https://doi.org/10.1037/edu0000367),
[Brunmair and Richter (2019)](https://doi.org/10.1037/bul0000209), and
[Firth, Rivers, and Boyle (2021)](https://doi.org/10.1002/rev3.3266).

### Worked examples and expertise

A mathematics meta-analysis covering 43 articles, 55 studies, and 181 effects found an average worked
example benefit of `g = 0.48`. Correct examples performed better than incorrect-only or mixed examples;
adding self-explanation prompts was a negative moderator in that synthesis. A separate meta-analysis
of the expertise-reversal effect found that high assistance favored low-prior-knowledge learners
(`d = 0.505`), while high-prior-knowledge learners did better with lower assistance (`d = -0.428`),
with substantial heterogeneity.

Product/content implications:

- Store a correct worked solution for novice feedback.
- Keep the problem visible before its solution and require an attempt first.
- Fade scaffolding when repeated performance—not confidence alone—supports it.
- Do not force explanation prompts into every worked example.

Sources: [Barbieri et al. (2023)](https://doi.org/10.1007/s10648-023-09745-1) and
[Tetzlaff et al. (2025)](https://doi.org/10.1016/j.learninstruc.2025.102142).

### Generation, self-explanation, and transfer

Generation and self-explanation have positive average effects, but task design matters. A general
self-explanation meta-analysis reported `g = 0.55`. A mathematics synthesis found small-to-moderate
immediate effects for procedural knowledge (`0.28`), conceptual knowledge (`0.33`), and transfer
(`0.46`), but only nine experiments included delayed tests; delayed procedural (`0.13`) and conceptual
(`-0.05`) effects were nonsignificant, while delayed transfer was `0.32`. A transfer meta-analysis of
retrieval practice found `d = 0.40` across 192 effects, with marked variation by transfer type and
practice design.

This can support separately designed exercises asking for reasons, examples, proof plans, and new
applications. Study's fixed review queue does not currently add those prompts, and one fluent
explanation or nearby variant must not be treated as broad transfer.

Sources: [Bertsch et al. (2007)](https://doi.org/10.3758/BF03193441),
[Bisra et al. (2018)](https://doi.org/10.1007/s10648-018-9434-x),
[Rittle-Johnson, Loehr, and Durkin (2017)](https://doi.org/10.1007/s11858-017-0834-z), and
[Pan and Rickard (2018)](https://doi.org/10.1037/bul0000151).

### Difficulty and sleep are boundaries, not scheduler tricks

“Desirable difficulty” is conditional: manipulations that depress current performance can improve
later learning, but high element interactivity and cognitive load can reverse the effect. Study should
not chase a universal failure rate or make sessions hard for their own sake. Failure is useful only
when the task remains interpretable and corrective feedback closes the gap.

Sleep deprivation before learning has a larger average association with impaired memory than sleep
deprivation after learning, and even partial restriction shows a smaller but reliable average harm.
These findings justify avoiding product language that glorifies late-night cramming. They do not
justify sleep-stage-aware scheduling, medical advice, or inferring sleep from response time.

Sources: [Soderstrom and Bjork (2015)](https://doi.org/10.1177/1745691615569000),
[Chen et al. (2018)](https://doi.org/10.3389/fpsyg.2018.01483),
[Newbury et al. (2021)](https://doi.org/10.1037/bul0000348), and
[Crowley et al. (2024)](https://doi.org/10.1016/j.neubiorev.2024.105929).

## What Study deliberately does not claim

- The self-calibrating scheduler is not an optimal-memory algorithm.
- A calibrated self-grade probability is not a calibrated probability of objective correctness.
- Completing the due queue is not proof of mastery.
- Self-grades are not objective correctness labels.
- Confidence is not knowledge.
- Remembering a statement is not the same as understanding or proving it.
- Reconstructing a stored proof is not the same as solving a novel problem.
- Interleaving is not equivalent to randomization.
- A same-session retry is not a substitute for relearning on a later day.
- Effect sizes from vocabulary, prose, school algebra, or laboratory tasks do not transfer unchanged
  to advanced mathematics.
- Population-average effects do not guarantee benefit for one learner or one topic.

## How to evaluate future review changes

Prefer delayed, behavior-based outcomes over engagement metrics. A credible evaluation should:

1. Predefine a retention horizon and a primary outcome.
2. Include unseen but structurally related problems, not only repeated prompts.
3. Separate statement retention, proof reconstruction, routine procedure, and transfer.
4. Stratify by prior knowledge and task family where sample size permits.
5. Compare against a plausible alternative such as restudy, existing scheduling, or blocked practice.
6. Preserve authored order unless sequence is the tested intervention.
7. Report uncertainty, attrition, exposure time, external assistance, and missing attempts.
8. Avoid tuning and evaluating on the same review history.

Until Study has such evidence, scheduler changes should be described as engineering hypotheses.
