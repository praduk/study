# AGENTS.md

These instructions apply to the entire Study repository. They are operational rules for both code
changes and AI-assisted mathematics authoring. Preserve user work, be explicit about uncertainty,
and prefer a smaller verified change over a broad speculative one.

## Product invariants

- The product name is **Study** in prose and user-visible UI.
- Study is a single-owner, local-first web application. It has no user/account model.
- With no arguments, `python study.py` binds only to `127.0.0.1`, bypasses the password, and opens a
  browser. `--server` does not open a browser and must refuse to start without a password hash.
- All application data is rooted at `data/` relative to `study.py`. Do not redirect authored data
  into a database or an external service.
- `data/` is versioned. Do not add a blanket ignore for it. Only live session database files under
  `data/runtime/` are deliberately ignored.
- Server-mode password protection is not transport encryption. Do not imply that HTTP is safe for
  public exposure; recommend HTTPS or a trusted VPN.
- Reading and review must remain usable on a phone. Authoring is desktop-oriented and hidden in the
  narrow layout.
- MathJax and Excalidraw runtime assets are copied from pinned packages and served locally. Do not
  introduce a CDN dependency without an explicit product decision.
- Review and PDF export use authored library order. Do not silently randomize the queue or export.
- Spacing is evidence-based; the exact scheduler constants are not. Never describe the current
  formula as scientifically optimal, FSRS, or a validated retention model.
- General retrieval practice is well supported, but direct mathematics-specific evidence for a
  retrieval-over-restudy advantage is currently sparse and inconclusive. Do not erase this caveat.

Read `README.md`, `docs/SEARCH.md`, `docs/LEARNING_SCIENCE.md`, and
`docs/research/report-source.md` before changing behavior or claims in those areas.

## Repository map

- `study.py`: launcher.
- `study_app/cli.py`: local/server launch behavior and password setup.
- `study_app/app.py`: FastAPI routes, authorization, uploads, diagrams, Git, and export endpoints.
- `study_app/store.py`: the authoritative content schema, canonical tags, ordering, and file writes.
- `study_app/library_validation.py`: fail-closed structural, identifier, path, and file validation.
- `study_app/search_index.py`: immutable full-text and lexical-scope reference indexes.
- `study_app/review.py`: prompts, queue order, attempt logging, and scheduling.
- `study_app/export.py`: Markdown-to-HTML and Playwright PDF rendering.
- `frontend/app/` and `frontend/components/`: responsive UI, editor, reader, and review flow.
- `frontend/scripts/copy-vendor.mjs`: offline MathJax and Excalidraw asset generation.
- `data/library.json`: folder and entry metadata.
- `data/macros.json`: global LaTeX macros.
- `data/content/`: Markdown formulations, proofs, and solutions.
- `data/media/`, `data/diagrams/`, and `data/excalidraw/`: media and editable diagram sources.
- `data/review.json` and `data/review-log.jsonl`: review state and history.

## Before changing mathematical content

1. Read the target entry in `data/library.json` and every Markdown file named by its formulations
   and supplements.
2. Read `data/macros.json`; reuse the author's notation instead of introducing duplicate commands.
3. Resolve every `@tag`, canonical tag, and prerequisite in the existing library from the entry's
   folder. Missing or ambiguous references are errors to investigate, not names to guess.
4. Identify the authority for the requested fact: a user-supplied source, an authoritative text,
   or a primary paper. If no authority is available and correctness is not independently
   demonstrable, stop and ask rather than filling the gap.
5. State the intended change and preserve the author's scope, notation, order, and level unless the
   user asked to change them.

Do not treat existing content as correct merely because it is present. Conversely, do not replace a
valid convention with a preferred convention without a mathematical reason and user authorization.

## Never invent

- Never fabricate a theorem name, definition, hypothesis, proof step, counterexample, citation,
  author, page, quotation, DOI, or canonical tag.
- Never make an unproved converse, silently strengthen or weaken hypotheses, or turn a convention
  into a theorem.
- Never claim two formulations are equivalent until both implications and all domain assumptions
  have been checked.
- Never repair a proof by changing the theorem statement without reporting the mismatch.
- Never cite a source not actually inspected. If a source is secondary, label it as such; if a
  statement is an internal derivation, say so.
- Never infer the contents of an unread image or diagram. Inspect the source or state that it could
  not be verified.
- Never manufacture review progress, grades, elapsed time, confidence, or log records.
- Never use a confident tone to hide uncertainty. Record the precise unresolved point and what
  evidence would resolve it.

## Content schema and namespace rules

Treat IDs as stable opaque identifiers. Do not rename existing folder, entry, variant, or asset IDs.
Prefer the running Study API/editor for creating records because it generates IDs and updates
metadata atomically. If direct offline creation is necessary, use collision-resistant lowercase
UUID hex IDs and update the JSON and Markdown paths together.

Deletion is deliberately guarded. Entry deletion requires confirmation. Empty folders may be
deleted directly after confirmation; deleting a non-empty folder must use the explicit recursive
path and identify the entire affected subtree. Commit metadata before cleaning up files so a failed
unlink can leave only an inert orphan, never a live record pointing at a missing file. Do not remove
a media or diagram file while any surviving asset record or Markdown content still references it.
Historical review state and the append-only review log are retained when authored content is deleted.

### Folders

A folder has `id`, `name`, `slug`, `parent_id`, `order`, and `review_enabled`. Its namespace is
computed from ancestor slugs, root first. For example, folders with slugs `math` and `algebra`
produce `math:algebra`.

- A slug must match `^[a-z][a-z0-9-]*$` and be at most 64 characters.
- A folder chain may contain at most 64 levels.
- Sibling folder slugs must be unique.
- `parent_id` must name an existing folder or be `null`; cycles are invalid.
- Disabling review on a folder effectively disables its entire descendant branch.
- Moving or renaming a folder changes all descendant canonical tags and can rebind a short `@tag`
  by changing its lexical scope. Audit every affected Markdown reference; never update by blind text
  replacement.

### Entries

Every entry, including a problem, has an `id`, `folder_id`, `kind`, `title`, `tag`, `header`, `order`,
`review_modes`, `problem_family`, `confusable_with`, `formulations`, `supplements`, and `assets`.

Allowed kinds are:

| Code | Meaning | Alternative formulations | Supplement |
| --- | --- | --- | --- |
| `ax` | Axiom | yes | none |
| `df` | Definition | yes | none |
| `rk` | Remark | no | none |
| `th` | Theorem | yes | proof (`pf`) |
| `pb` | Problem | no | solution (`sl`) |

- Tags and subtags follow `^[a-z][a-z0-9-]*$`; entry tags are at most 80 characters.
- An entry tag must be unique among entries with the same folder and kind. Do not rely on that
  narrow rule to create confusing cross-kind collisions.
- The canonical entry tag is `<folder-namespace>:<kind>:<tag>`.
- The custom `header` is rendered before the body and is visible before a review attempt. Use it for
  scope, prerequisites, provenance, or orientation—not an answer that defeats retrieval.
- `order` determines reading, export, and review order within the folder.

### Formulations and supplements

Each entry must have at least one formulation. Maintain exactly one main formulation in each group:

- The main formulation has `main: true`, `subtag: null`, and the entry's canonical tag.
- A non-main formulation has `main: false` and a unique nonempty subtag. Its canonical tag appends
  `:<subtag>`.
- Only `ax`, `df`, and `th` may have alternative formulations.
- Only `th` may contain `pf` supplements and only `pb` may contain `sl` supplements.
- The main proof or solution appends `:pf` or `:sl`; each non-main alternative also appends its
  unique subtag.
- Promoting a variant to main removes its subtag. The application assigns `standard` to a displaced
  former main that lacked one; direct edits must preserve the same invariant.
- A variant's `file` must remain below `data/`, normally
  `content/<entry-id>/<variant-id>.md`, and must name an existing UTF-8 Markdown file.

Examples:

```text
math:algebra:df:group
math:algebra:df:group:category
math:algebra:th:lagrange:pf
math:algebra:th:lagrange:pf:action
math:algebra:pb:z12-subgroups:sl
math:algebra:pb:z12-subgroups:sl:generators
```

### Scoped `@tag` references

- A short reference resolves in deterministic stages: direct current folder, current descendants,
  direct parent, newly visible sibling subtrees, then the same two stages at each higher parent.
  If the originating top-level tree has no match, use one final repository-wide stage over all other
  top-level trees. Local and higher-level stages always shadow this global fallback.
- The first nonempty stage shadows every farther stage. If it contains multiple targets, the
  reference is deliberately ambiguous. Never choose by title, depth, or authored order; use a
  canonical tag.
- Fully qualified canonical references resolve exactly. Alternatives, proofs, and solutions may be
  addressed with their subtag components.
- `@[replacement text]tag` resolves the same tag while displaying the replacement text inline. The
  replacement is nonempty, single-line plain text without square brackets. It never replaces the
  resolved entry title in the preview, and missing or ambiguous references show the full authored
  form.
- Parse references only from Markdown text nodes. Never interpret an `@` inside code, a link, an
  email address, or mathematics.
- Search and resolution are read-only. Normal writes must invalidate the in-memory index; Git Pull
  must rebuild it before returning. Preserve the bounded direct-file-change check documented in
  `docs/SEARCH.md`.

### Review metadata

Review tasks are fixed, not author-selectable:

- When the user asks to populate Study or create new content, keep every newly created entry out of
  review initially unless the user explicitly asks to include it. Review inclusion is currently
  folder-scoped: use a review-disabled destination without disabling review for pre-existing content,
  and report the constraint if the requested destination is already review-enabled.
- Axioms, definitions, and remarks use `statement`.
- Theorems use `statement`, followed by internal mode ID `proof-plan` when a main proof exists. The
  user-visible task is “Proof of theorem” and requires the complete proof, not merely a plan.
- Problems use `solve` when a main solution exists and remain out of review until then.

The store derives `review_modes`; never hand-author a different list. `problem_family` and
`confusable_with` are free-form metadata today; the scheduler does not interpret them. Historical
state for removed modes may remain in `review.json` or the append-only log, but it must not re-enter
the queue or be silently reclassified.

Do not hand-edit `data/review.json` or `data/review-log.jsonl` as part of a content correction. Card
IDs are `<entry-id>::<mode>`; changing an entry ID or mode can orphan historical state.

## Markdown, mathematics, and assets

- Use portable CommonMark for meaning that must survive PDF export. The web reader also supports
  GitHub-flavored Markdown, but the current PDF path does not implement every GFM extension. Raw HTML
  is disabled in PDF export and must not carry essential meaning.
- Use `$...$` for inline math and `$$...$$` for display math. `\(...\)` and `\[...\]` also work.
- Global MathJax macro keys contain ASCII letters only and omit the leading backslash. Values are a
  replacement string or the MathJax array form. Check every changed macro across the entire
  library; a global change can break unrelated entries.
- Define every symbol before use unless it is genuinely standard at the target level. Preserve
  distinctions such as element versus subset, equality versus isomorphism, and implication versus
  equivalence.
- Keep prose outside display math. Use aligned displays only when alignment clarifies the argument.
- Give images meaningful alt text. Lightness inversion is opt-in metadata for dark mode; verify it
  does not make color-dependent meaning ambiguous.
- Use the application endpoints/editor to add images and diagrams. Handwritten media paths,
  Excalidraw comments, commutative tokens, or asset records can easily become orphaned.
- Before deleting or replacing an asset, search `data/library.json` and all Markdown for its source,
  preview, ID, and filename.

## Mathematics quality standard

### Axioms and definitions

- State the ambient structure and quantify every variable.
- For a definition, make necessity and sufficiency explicit; do not give only examples.
- Check degenerate and boundary cases. Add a justified example and nonexample when they reveal the
  boundary better than prose.
- If conventions vary by source, state the chosen convention and its consequence.

### Theorems and proofs

- Match the proof to the exact main formulation, including finiteness, regularity, choice,
  nonemptiness, and domain assumptions.
- Resolve every dependency and check for circular reasoning.
- Justify each nontrivial implication; a familiar lemma still needs either a proof or a resolvable
  canonical/source reference appropriate to the library's level.
- Check equality conditions, signs, endpoints, exceptional characteristics, empty cases, and
  quantifier order where relevant.
- Independently reconstruct the argument before editing the stored proof. If the theorem is false,
  present the smallest counterexample and stop before rewriting scope.

### Problems and solutions

- Ensure the prompt is self-contained, has enough hypotheses, and does not leak the solution through
  its header.
- Solve independently before reading the stored solution when performing a review audit.
- Verify intermediate algebra, domains, units, branch choices, and the final result by substitution,
  a second method, or a counterexample search as appropriate.
- Keep hints separate from the main solution when possible. A worked solution should expose the
  strategy and warrants, not merely the final manipulation.

### Alternative formulations

- Verify equivalence in both directions under the same assumptions.
- Explain the purpose of the alternative—different primitives, categorical form, computational
  criterion, or another genuine viewpoint.
- Give it a short descriptive subtag. Do not use `alternative-1` or invent a school/source label.

## Review science guardrails

The exact implemented flow and formulas are documented in `docs/LEARNING_SCIENCE.md`. Preserve these
distinctions in UI copy, code comments, and documentation:

- Retrieval must occur before answer exposure; confidence is recorded after the attempt and before
  feedback.
- Overt answers are preferred for accountability, but think-only retrieval remains available.
- Feedback includes only the answer family for the active task: formulations for statement recall,
  proofs for theorem proof recall, or solutions for problems.
- Grades are self-reports, not correctness judgments from Study.
- An Again response creates an in-session retry and a ten-minute due time. Longer intervals are a
  transparent heuristic based on prior stability, difficulty, and grade.
- Authored order is a curricular control. It can be used to arrange deliberate interleaving among
  confusable problem types, but Study does not currently generate or optimize that arrangement.
- Alternative variants are not separate cards. They appear only as alternatives to the matching
  statement, proof, or solution after reveal.
- Do not use immediate fluency, time-on-task, confidence, or a streak as proof of durable learning.

When changing the scheduler or prompts, update both learning-science documents and add tests for
queue order, folder inheritance, attempt/reveal gating, formula boundaries, and retry placement.

## Verification

For any content change:

1. Parse `data/library.json` and `data/macros.json`.
2. Confirm every folder, entry, variant, supplement, and asset reference resolves under `data/`.
3. Confirm sibling slug uniqueness, per-folder/per-kind entry tag uniqueness, acyclic parents, one
   main per formulation/supplement group, and unique required subtags.
4. Search for stale canonical tags and orphaned asset filenames.
5. Resolve every affected `@tag` from its containing folder and reject unexpected rebinding,
   ambiguity, or missing targets.
6. Render the changed entry in both themes. Exercise every changed macro and inspect small-screen
   reading/review if layout-sensitive.
7. For proof/solution changes, perform the independent mathematical checks above and report any
   assumption that remains source-dependent.

For code or schema changes, run:

```sh
python -m ruff check study.py study_app tests
python -m pytest
cd frontend && npm test && npm run lint && npx tsc --noEmit && npm run build
```

Also run a local smoke test for affected API/UI paths. Changes to MathJax, Markdown, media, diagrams,
or export require a representative PDF export and visual inspection. Changes to launch/auth require
separate local-mode and server-mode checks; do not weaken loopback, password, Host, origin, CSRF,
cookie, or path-containment protections.

Before finishing, inspect `git diff` and `git status`, preserve unrelated changes, and run
`git diff --check`. Do not commit, push, pull, delete user content, rewrite review history, or perform
a destructive Git operation unless the user explicitly requested it. Report exactly which files
changed, which checks ran, and which risks or uncertainties remain.
