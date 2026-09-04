# Study

Study is a local-first web application for writing, organizing, reading, and reviewing
mathematics. Its Python backend stores the library as Markdown and JSON under `data/`; the
responsive web interface supplies MathJax, Vim editing, diagrams, image handling, PDF export,
and an evidence-informed review workflow.

Study has one library and no user accounts. Local mode is loopback-only and skips the password.
Server mode is password-protected and stores revocable sessions.

## What Study supports

- Nested folders with computed namespaces such as `math:algebra`.
- Axioms (`ax`), definitions (`df`), remarks (`rk`), theorems (`th`), and problems (`pb`).
- Alternative formulations for axioms, definitions, and theorems, with one main formulation.
- Proofs (`pf`) for theorems and solutions (`sl`) for problems, including tagged alternatives.
- GitHub-flavored Markdown in the web reader, local MathJax, global LaTeX macros, and custom
  Markdown headers. PDF export currently uses portable CommonMark.
- A CodeMirror editor with Vim keybindings and a live preview. Escape stays inside Vim; `:q` closes
  the editor explicitly.
- Image upload or clipboard paste, selectable width, and optional HSL-lightness inversion in dark
  mode. Hue and saturation are preserved; this is not an RGB color inversion.
- Embedded Excalidraw scenes, a shared Excalidraw template library, LaTeX insertion into drawings,
  and a grid-based commutative-diagram editor.
- Exact-position insertion controls for entries and folders, drag-and-drop ordering, and a tree
  picker for moving a folder under another folder. Canonical namespaces are recomputed after a move.
- Confirmed deletion for entries and folders. Deleting a non-empty folder requires typing its name
  and removes the complete subtree; shared media files are retained while anything still uses them.
- Scoped `@tag` references that expand from the current folder through progressively broader
  subtrees, then fall back across the full library, with fully rendered hover/focus/tap previews
  and a `Cmd/Ctrl+Shift+K` insertion picker.
- A hideable, resizable library panel and an uncluttered single reading panel.
- Fast full-library search over titles, tags, headers, formulations, proofs, and solutions.
- PDF export for the whole library or a folder, recursively or not, filtered by entry type, in the
  same authored order as the library.
- A phone layout intended for reading and review. Editing controls are deliberately hidden on
  narrow screens.
- Local Git controls that commit only authored `data/`, plus fast-forward-only pull when the entire
  worktree is clean. Fetched Study data is validated in a detached checkout before the current
  branch advances, and the browser reloads the library before editing is re-enabled.

## Install

Requirements:

- Python 3.10 or newer
- Node.js 22.13 or newer and npm
- A Chromium browser installed for Playwright PDF export

From the repository root:

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'

cd frontend
npm ci
npm run build
cd ..

python -m playwright install chromium
```

`npm ci` and `npm run build` copy the pinned MathJax package and Excalidraw fonts into the ignored
`frontend/public/vendor/` directory. Study serves those assets locally; normal reading, review, and
typesetting do not depend on a CDN.

On Windows PowerShell, activate the environment with `.venv\Scripts\Activate.ps1` instead.

## Run locally

```sh
python study.py
```

With no arguments, Study binds to `127.0.0.1`, waits for the health check, and opens
`http://127.0.0.1:8765` in the default browser. A password is not requested in this mode, and the
server is not reachable from another device.

The installed command is equivalent:

```sh
study
```

## Run for phone access

First create a password hash:

```sh
python study.py --set-password
```

Study accepts any non-empty password and writes only an Argon2 hash to the ignored, owner-readable
`config.local.toml`. Add the exact LAN host or HTTPS hostname used by the browser to
`allowed_hosts`, then start server mode:

```sh
python study.py --server
```

Server mode binds to `server_host` and does not open a browser. It uses an HTTP-only, SameSite
session cookie by default, same-origin checks, CSRF tokens for mutations, exact host allowlisting,
and login throttling. These controls do **not** encrypt traffic. For access beyond a trusted local
network, put Study behind HTTPS or a trusted VPN and set `secure_cookie = true`. Do not expose the
default HTTP listener directly to the public Internet.

Configuration is read from `config.toml`, then overlaid by `config.local.toml`. A separate file can
be selected with `--config PATH`; for example, `server.toml` is overlaid by `server.local.toml`.
Important fields are:

```toml
[study]
port = 8765
server_host = "0.0.0.0"
allowed_hosts = ["127.0.0.1", "localhost", "[::1]", "192.0.2.10"]
session_days = 30
secure_cookie = false
max_upload_mb = 12
max_image_megapixels = 32
```

The data location is intentionally not configurable: authored material and runtime state always
live in `data/` beside `study.py`.

Keep `password_hash` in `config.local.toml`, not the tracked configuration. Study is a single-owner
application; password protection is not multi-user authorization.

## Content model and tags

Folder slugs form the namespace from the root down. Every entry has a type and tag:

```text
math:algebra:df:group
```

An alternative formulation adds its subtag:

```text
math:algebra:df:group:category
```

The main formulation uses the entry tag without a subtag. Proofs and solutions append their own
kind and, for a non-main alternative, a subtag:

```text
math:algebra:th:lagrange:pf
math:algebra:th:lagrange:pf:action
math:algebra:pb:z12-subgroups:sl
math:algebra:pb:z12-subgroups:sl:generators
```

Slugs, tags, and subtags start with a lowercase letter and then use lowercase letters, digits, or
hyphens. Moving or renaming a folder changes computed canonical tags for its descendants; references
written inside Markdown are not rewritten automatically. Folder nesting is capped at 64 levels,
which keeps every valid canonical reference within the bounded API and prevents pathological trees.

### Scoped references and search

In ordinary Markdown prose, `@group` resolves in the entry's own folder first, then its descendant
subtree. Study next checks the direct parent and the sibling subtrees exposed at that level, and
repeats outward through real ancestors. If the originating top-level tree has no match, one final
stage checks every other top-level tree. The first nonempty stage wins, so a local or higher-level
target always shadows global matches. Alternative formulations and supplements use the same
concise syntax, such as `@group:category`, `@lagrange:pf`, or `@lagrange:pf:action`.

If the first nonempty stage contains more than one matching target, Study marks the reference
ambiguous and does not guess or continue outward. The insertion picker uses a fully qualified tag
such as `@math:algebra:df:group` in that case. A resolved reference displays the entry title while
leaving the authored `@tag` unchanged; missing and ambiguous references remain visible as their
exact source text. References are recognized only in Markdown text—not in code, links, email
addresses, or mathematics. Resolved hover previews use the same Markdown, MathJax, image,
Excalidraw, and commutative-diagram renderer as the reader.

Global search and the insertion picker use an immutable in-memory index. Study precomputes folder
ancestry, preorder subtree intervals, direct/canonical reference buckets, and trigram posting lists;
it reads each Markdown file once per index build, verifies exact substrings after candidate
filtering, and uses deterministic ranking. App
writes invalidate the cache immediately, Pull rebuilds it synchronously, and direct file edits are
detected within 250 ms. The complete contract is in [`docs/SEARCH.md`](docs/SEARCH.md).

## Markdown and media

Use `$x$` for inline mathematics and `$$x$$` for display mathematics. `\(...\)` and `\[...\]` are
also accepted. Macro names and definitions are global and stored in `data/macros.json`.

Images inserted through the editor are normalized to PNG and stored by content hash. The generated
Markdown carries display settings in its URL fragment:

```markdown
![Cayley graph](/media/0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef.png#width=70&invert=lightness)
```

Use the editor for images and diagrams whenever possible so the source file, preview, asset
metadata, width, and entry association remain consistent. Excalidraw source remains editable under
`data/diagrams/`; its Markdown includes a preview and an `excalidraw` source comment. Commutative
diagrams use a stored JSON source and an insertion token such as:

```text
[[commutative:0123456789abcdef0123456789abcdef|width=76]]
```

Raw HTML is not a portable content format in Study and is disabled by the PDF renderer. The web
reader supports GitHub-flavored additions such as tables; the PDF path currently renders CommonMark,
so do not put essential meaning in a web-only extension without checking the export.

## Review, exactly as implemented

Each fixed review task of an entry is a separate card: axioms, definitions, and remarks have
Statement; theorems have Statement and, when a main proof exists, Proof of theorem; problems have
Solve once a main solution exists. Review loads new or due cards in authored
order in batches of at most 200. After a batch is exhausted, it fetches the next due batch and only
reports completion after a fresh request returns no cards. The flow for each card is:

1. Read the prompt and, for `solve` or `proof-plan`, the main problem or theorem statement.
2. Make an attempt. Writing it is the default; its Markdown/MathJax preview can be toggled before
   submission. “Think-only review” is available but must still be an honest retrieval attempt.
   Record any hint use.
3. Rate confidence as Unsure, Somewhat, or Confident before revealing the stored answer.
4. Reveal only the matching answer and its alternatives: formulations, proofs, or solutions.
5. Compare hypotheses, conclusions, dependencies, strategy, and justification—not wording alone.
6. Self-grade with Again, Hard, Good, or Easy. Keys `1` through `4` select those grades.

This is self-assessment, not automatic proof checking. A familiar-looking answer is not evidence
that the attempted statement, proof, or solution was correct.

Due cards follow authored order: root folders, each folder's direct entries, then its child folders,
recursively. Entries and sibling folders use their stored `order`; theorem statement precedes proof.
Cards that are not due are skipped without disturbing the relative
order of eligible cards. Disabling a folder excludes that folder and all descendants, even if a
descendant's own checkbox is enabled.

An Again grade sets the next due time to ten minutes and also inserts a retry after up to three
currently available intervening cards. Hard, Good, and Easy update a per-card stability estimate
and schedule an integer-day interval. The formulas and constants are transparent in
[`docs/LEARNING_SCIENCE.md`](docs/LEARNING_SCIENCE.md); they are a product heuristic, not a
scientifically validated optimum.

The scientific distinction matters: spacing has robust direct evidence in mathematics, with a
recent meta-analysis finding a small-to-medium benefit. General retrieval-practice evidence is
substantial, but the same mathematics meta-analysis found too little math-specific evidence to
establish a consistent retrieval-over-restudy advantage. Study therefore uses retrieval as a
useful practice mechanism, not as a claim that flashcards alone produce mathematical mastery. See
the [learning-science rationale](docs/LEARNING_SCIENCE.md) and
[source-provenance ledger](docs/research/report-source.md).

## Data and Git

All library data is rooted at `data/` relative to `study.py`:

```text
data/
  library.json                 folder, entry, variant, order, and asset metadata
  macros.json                  global MathJax macros
  review.json                  current per-card schedule and pending attempts
  review-log.jsonl             append-only graded-attempt history, created on first grade
  content/<entry>/<variant>.md Markdown formulations, proofs, and solutions
  media/                       normalized image and drawing previews
  diagrams/                    Excalidraw and commutative-diagram sources
  excalidraw/                  shared Excalidraw library
  exports/                     generated PDFs
  runtime/                     ephemeral export work and the session database
```

The `data/` directory is intentionally not ignored. Authored content, diagrams, macros, and review
history can be committed. The sole persistent exception is the session SQLite database and its
journal files, because they contain live authentication tokens. `config.local.toml`, dependencies,
build output, and copied vendor assets are also ignored.

The in-app Commit action commits only `data/` while preserving unrelated staged work. To make that
scope enforceable, this narrowly scoped action does not run repository hooks; use normal Git when a
hook-controlled commit is required. Pull refuses a dirty worktree, rejects upstream session or
transient runtime files, and uses fast-forward-only mode; it never creates a merge commit or
discards work.
Study validates folder, entry, variant, review-mode, asset, and Markdown-file invariants when loading
the library so a broken manual edit or pull fails visibly instead of silently becoming empty content.

## Development checks

Run the checks relevant to a change:

```sh
python -m ruff check study.py study_app tests
python -m pytest

cd frontend
npm run lint
npm run build
```

For changes to Markdown rendering, MathJax, diagrams, or PDF export, also launch Study, inspect both
themes and the phone layout, and render a representative PDF. See [`AGENTS.md`](AGENTS.md) for the
repository and mathematical-content verification rules.
