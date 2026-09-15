# Scoped deletion follow-up — 14 September 2026

Normal deletion in the current v2 format no longer makes a complete library backup or reparses and validates every entry. It moves only the deleted directories and exclusively owned legacy assets into recoverable transaction storage. Shared assets remain supported; no content or asset migration was needed.

The requested pull completed before this implementation and reported that the checkout was already up to date. This follow-up builds on the earlier, uncommitted performance improvements. The owner's authored data and review history remain unchanged; every destructive test and measurement used disposable copies.

## What the new transaction guarantees

- The starting metadata snapshot must already have passed full validation, and all recorded file/directory signatures must still match. Cold or externally changed data still receives full validation before use.
- Only the selected entry, empty folder, or explicitly confirmed subtree is detached. Survivor sidecar bytes and sparse ordering ranks stay unchanged. Deep logical subtrees and legacy external asset files are handled explicitly.
- Before commit, topology and file signatures prove that only the declared roots moved. Unexpected edits abort the deletion. Rollback restores detached content and preserves conflicting new files for inspection.
- A durable prepared journal precedes any authored move. An unfinished deletion rolls back at startup; a committed deletion remains deleted.
- Committed journals retain deleted entry IDs until schedules, pending attempts, and history are durably purged. Restoring the same authored ID cannot silently restore its deleted history. New grading waits for a durable acknowledgment.
- Acknowledged trash is removed after the HTTP response. Cleanup first retires the active journal by rename, so an interrupted recursive unlink cannot block future reads. Conflicted rollback material and unpublished preparation directories remain inert under runtime storage.

The operation still checks library-wide signatures and any surviving asset references. It also refreshes the reader and search index after deletion. This change removes the expensive backup and full parse from ordinary deletion; it does not make deletion independent of library size.

## Measurements

The browser comparison uses the same 242-folder, 1,454-entry, 2,330-Markdown library, Chromium desktop viewport, frozen read-only Git root, and three synthetic targets per action. The baseline is the source after the earlier performance improvements but before scoped deletion. Timers start at the final confirmation click and end after the dialog closes, the correct surviving selection appears, and math/linked-item reads settle. Required human typing for subtree confirmation occurs before the timer.

| Action | Before | After | Less time |
|---|---:|---:|---:|
| Delete selected entry | 3,407.76 ms | 1,149.75 ms | 66.3% |
| Delete empty folder | 3,436.23 ms | 1,155.57 ms | 66.4% |
| Delete confirmed subtree (2 folders, 3 entries) | 3,460.12 ms | 1,197.37 ms | 65.4% |

All nine actions per version passed. There were no browser errors, HTTP errors, or visible error messages. [Raw before](browser-deletion-before.json) / [raw after](browser-deletion-after.json); inspected [entry result](desktop-1-deleted-entry.png) and [subtree result](desktop-3-deleted-subtree.png). Measurements are sequential local observations, not production or percentile guarantees. Browser fixtures have no assets; the additional API run exercises an entry with an image, both diagram formats, and synthetic review history, using the compatible full-library response.

The final [API run](api-after.json) completed all 75 recorded action groups. Deleting the entry with assets and review history took **819.30 ms**, and the following empty-folder deletion took **469.82 ms**. These are single observations with the full-library response and synchronous TestClient background completion; they are not the same timer as the browser measurements. The complete temporary library passed validation afterward. A representative [PDF export](api-after.pdf) took **523.51 ms** and its [rendered page](pdf-export.png) was visually inspected.

## Verification and changed files

- Python lint passed; the final full Python suite passed **329 tests in 24.02 seconds** ([output](python-tests.txt)).
- All **47 frontend tests**, frontend lint, TypeScript checking, and the frontend build passed ([build output](frontend-build.txt)); the rebuilt shipped bundle is unchanged from the immediately preceding implementation.
- The real library passed `python study.py --check-data`: v2, 242 folders, 1,454 entries, 2,330 Markdown files.
- Final `git diff --check` passed. Git status for `data/` is empty. No authored data or review history was changed, and no commit, push, or deployment was performed.


Regression coverage includes forbidding full-library backup/validation during warm entry, empty-folder, and subtree deletion and their following reader/search requests. It also covers abrupt process exit before and after commit, interrupted preparation and trash cleanup, direct edits in surviving or detached content, conflicting recovery paths, old unfinished write journals, malformed tombstone IDs, review log/state write failures, restored IDs, and acknowledgment flush failure.

Implementation files changed in this follow-up:

- `study_app/scoped_deletion.py` — new scoped journal, safe moves, recovery, and cleanup.
- `study_app/store.py` — deletion planning, signature proof, trusted cache update, and journal APIs.
- `study_app/review.py` — durable deletion intent and review cleanup acknowledgment.
- `study_app/app.py` — startup recovery cleanup and background trash removal after DELETE.
- `tests/test_deletion_performance_contracts.py` — adapted and extended deletion regressions.
- `tests/test_scoped_deletion_api.py`, `tests/test_scoped_deletion_process.py`, `tests/test_scoped_deletion_review.py`, and `tests/test_scoped_deletion_safety.py` — new API, crash, review, and transaction-conflict tests.
- `docs/STORAGE.md`, `docs/PERFORMANCE.md`, and this evidence directory — transaction contract, results, and reproducible evidence.

No frontend source, dependency, authored content, ID, asset ownership, or storage-format migration was needed for this follow-up. Version 1 keeps its existing deletion behavior. Other structural writes still use their existing recovery protocol.

## Reproduce

Keep a frozen copy of the immediately preceding source for `BEFORE`, and use the same clean checkout for read-only Git status in both runs. Both scripts create and mutate their own temporary data copy.

```sh
python scripts/benchmark_browser.py --source-root /path/to/BEFORE --git-root /path/to/clean-checkout --focus deletion --samples 3 --output /tmp/deletion-before.json
python scripts/benchmark_browser.py --source-root /path/to/UPDATED --git-root /path/to/clean-checkout --focus deletion --samples 3 --output /tmp/deletion-after.json
python scripts/benchmark_performance.py --source-root /path/to/UPDATED --git-root /path/to/clean-checkout --samples 7 --pdf --output /tmp/api-after.json
```

Run benchmarks sequentially without simultaneous tests or builds. The earlier broad performance report retains its historical API/everyday browser measurements; the measurements in this directory supersede its deletion results.
