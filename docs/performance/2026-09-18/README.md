# Study performance and bandwidth — 2026-09-18

The quick-drop failure is fixed by accepting native drags on `dragenter` as well as `dragover` and explicitly choosing the move operation. Successful moves expand their destination, and an immediate moving notice distinguishes a save from an ignored drop. Duplicate concurrent moves are blocked. Reader refreshes wait until the selected entry has its new namespace.

## Measurements

Paired API runs on disposable copies of the same 250-folder, 1,540-entry, 2,469-Markdown-file library, using local TestClient requests with gzip. The baseline imports Python code from commit `bae8ae5`; the after run imports this working tree. Git status uses the same checkout for both. No source data or review history was modified. Runs were sequential, without concurrent builds or test suites. Occasional small UI smoke checks are outside the timed request code. These are local request timings, not network latency or full browser-render timings.

| Action | Before (ms) | After (ms) | Samples before / after |
| --- | ---: | ---: | ---: |
| Move an entry | 3225.37 | 184.18 | 1 / 1 |
| Create an entry | 2768.68 | 1565.73 | 1 / 1 |
| Create a folder | 2754.06 | 1598.10 | 1 / 1 |
| Move a folder | 3231.29 | 1608.64 | 1 / 1 |
| Rename a folder | 2940.48 | 1686.31 | 1 / 1 |
| Rename an entry tag | 2924.08 | 1613.10 | 1 / 1 |
| Upload an image | 2963.70 | 1595.11 | 1 / 1 |
| Save an ordinary body edit | 156.04 | 160.84 | 3 / 3 |
| Refresh the library | 125.18 | 114.09 | 3 / 3 |
| Open an entry | 16.20 | 16.92 | 3 / 3 |
| Warm search | 1.59 | 1.49 | 3 / 3 |
| Load review queue | 36.87 | 39.27 | 3 / 3 |
| Open calendar | 63.37 | 66.04 | 3 / 3 |

Rows with three samples show medians; one-sample mutations are observations, not statistically established latency estimates. Search, ordinary content edits, reading, review, and calendar performance are broadly unchanged; the large gains are in structural writes and entry moves. Some remaining structural writes still take approximately 1.6–1.8 seconds because they validate and reparse the library.

The compressed navigation/bootstrap response decreased from **250,106 to 185,045 bytes (26.0%)** in this checkout. Decoded JSON decreased from **1,469,788 to 812,857 bytes (44.7%)**. Git status contributes checkout-dependent data to these responses. The move endpoint can now return only `{"ok":true}` (11 bytes), instead of an unused full snapshot; the UI still fetches its authoritative navigation snapshot afterward. Full legacy responses remain available to other clients.

The 144 KB drawing stylesheet is no longer included in the initial reading page; it loads with the drawing tool. Static files now honor matching ETags with an empty 304 response. Existing immutable caching for hashed bundles remains in effect.

## Write tradeoff

Following the owner's stated priority, the interactive app sets `recovery_backups=False`: it no longer copies the entire library before multi-file writes. Individual file writes remain atomic and validation remains in place. Abrupt interruption of a multi-file mutation is not guaranteed to roll back. Ordinary entry moves rename the entry directory without copying its assets, change its rank metadata, and retain a validated metadata cache only when exact file/signature checks succeed. Sparse-rank exhaustion and folder moves use the general write path. Same-folder drag reordering updates only the affected entry sidecar when a rank gap is available.

This is a performance policy for interactive authored writes, not a change to authentication, path containment, confirmed deletion, review scheduling, or stable record IDs. Existing journals from older writes can still be recovered; direct LibraryStore callers retain the conservative backup default.

## Verification

- 340 Python tests and 51 frontend tests passed; Python/frontend lint, TypeScript, and packaged frontend build passed.
- Real in-app browser: quick cross-folder drop; unselected entry into a collapsed destination; selected entry into an empty nested folder; entry-to-entry insertion; dropping outside the tree; updated URL and content; both themes; editor and on-demand drawing interface.
- Focused tests: no full-library copy/parse for ordinary moves, metadata failure rollback, concurrent external edits, sparse-rank exhaustion, duplicate-tag rejection, moved images/drawings, compact response compatibility, variant/proof deep links, review-stat parity, and static 304 responses.
- Library validation and final diff checks passed; authored data unchanged. A PDF containing mathematics and an image was exported and visually checked. The local server was restarted and the existing Algebra page reloaded successfully.

The full API audit also exercised review reveal/grading, uploads, drawing saves, deletion, and server-mode login/logout on disposable data. No commit, push, or production deployment was performed.

## Reproducing

Use `scripts/benchmark_performance.py --interactive --samples 3 --output RESULT.json`. Supply `--source-root` for another code/data snapshot and `--git-root` to keep the read-only Git comparison fixed. `before.json` and `after.json` contain all measured actions and sample values. The baseline ignores the new optional navigation/small-move parameters, reproducing its original response sizes.

See `changed-files.txt` for the complete working-tree file inventory, including generated frontend assets. Source changes cover store/API paths, library drag/navigation types, drawing stylesheet loading, tests, benchmark options, and the documented performance policy.
