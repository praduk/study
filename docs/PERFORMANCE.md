# Study performance review — 14 September 2026

The largest everyday improvements are saving edited items, reopening the library, review, and the calendar. Normal next/previous navigation was already under 100 ms on this computer; the changes reduce that further. Search and initial editor opening change little. A subsequent [scoped deletion implementation](performance/2026-09-14/scoped-deletion/README.md) removes ordinary v2 deletion's full-library backup and validation, bringing measured browser deletion to about 1.2 seconds.

The checkout was pulled before any implementation: `127a6d7` fast-forwarded to `8ce8622`. All comparisons use the pulled content: **242 folders, 1,454 entries, and 2,330 Markdown files**. The application data and review history were not edited by the performance work. Mutating tests ran against disposable copies. No changes were committed, pushed, or deployed.

## Everyday actions

Median elapsed time from browser interaction to readiness. Reduction is the percentage less time spent.

| Action | Before | After | Reduction |
|---|---:|---:|---:|
| Save an edited title and return to reader | 2,011 ms | 828 ms | 59% |
| Save edited body and return to reader | 2,031 ms | 795 ms | 61% |
| Reload the library — desktop | 463 ms | 306 ms | 34% |
| Next item — desktop | 81 ms | 65 ms | 19% |
| Previous item — desktop | 80 ms | 55 ms | 32% |
| Reload the library — phone layout | 463 ms | 284 ms | 39% |
| Next item — phone layout | 77 ms | 56 ms | 27% |
| Open calendar — desktop | 901 ms | 437 ms | 52% |
| Next calendar month — desktop | 549 ms | 86 ms | 84% |

## Deletion

These timings include the final confirmation click, deletion, library refresh, correct surviving selection, and settled math/linked items. Each row has three independent synthetic targets. The subtree contains two folders and three entries. The timed confirmation click follows the required typed folder-name confirmation; human typing time is excluded.

| Action | Original | Initial optimization | Scoped deletion |
|---|---:|---:|---:|
| Delete selected item, then show next item | 6,159 ms | 3,387 ms | 1,150 ms |
| Delete empty folder | 6,225 ms | 3,447 ms | 1,156 ms |
| Delete confirmed folder subtree | 6,112 ms | 3,448 ms | 1,197 ms |

The [initial deletion diagnosis](performance/2026-09-14/deletion-diagnosis.json) found about 1.1 seconds spent reparsing the library during review cleanup, after the write had already validated it. Actual log validation took about 10 ms in those samples. A discarded full response added roughly 2.9 MB of decoded JSON. The first implementation removed this redundant work but retained a complete backup and full validation. The subsequent scoped transaction removes those costs for ordinary v2 deletion, while preserving crash recovery and shared-asset guards. A fresh immediately preceding baseline measured 3,408 / 3,436 / 3,460 ms; the paired scoped results are 65–66% shorter. See the [follow-up report and raw evidence](performance/2026-09-14/scoped-deletion/README.md).

## How to interpret the measurements

- Host: Apple M4 Max, macOS 15.7.3 arm64, Python 3.10.18, Node 25.3.0. Results describe this local computer, not the deployed server or its network.
- API measurements use FastAPI TestClient and include the application, response serialization, and gzip where applicable, but exclude TCP/network/browser overhead. Reads normally use seven samples; after-idle checks use five with 300 ms between them. The table gives each actual sample count. Single-run structural operations are observations, not statistically established distributions.
- Browser measurements use real Chromium against a temporary local Uvicorn server and the shipped frontend. Each action has three samples per applicable viewport. Desktop is 1440×1000; phone is 390×844 with touch/mobile emulation on the same computer, not real phone hardware or throttled phone CPU.
- Browser contexts start fresh per sample; server metadata and search are prewarmed outside the measured section. “Cold” browser rows therefore mean a fresh browser context, not cold server startup. “Content ready” is visible entry content; “settled” also waits for math and linked-item reads. Readiness polling is 10 ms, and correctness assertions occur outside the timer.
- Typed search includes an intentional 20 ms per key, 100 ms total. The separate search-results row sets the query directly. Dialog reopening groups the supported macro, move, Git, and export dialogs; it is a sequence, not the latency of one dialog.
- Editor-save timers include save submission and return to a settled reader, including index-dependent reads. Direct API title-save timing measures only the write. An unchanged editor save sends no write request.
- Both versions use the same frozen clean checkout for read-only Git status. No Git commit, remote push, or application Git Pull was performed for timing. The user's requested checkout pull was performed once before editing; disposable Git tests check correctness separately.
- Review attempts and grades in the benchmark belong only to synthetic test entries. The benchmark never grades the owner's authored entries. Deletion uses only disposable data and preserves the application's confirmation flow.
- Raw JSON includes all samples, ranges, action identifiers, and browser API request counts. Small differences of a few milliseconds should not be read as robust gains; these runs are not a p95 or production-load study.

## What changed and why

1. **Read and review work:** internal readers inspect a locked validated metadata view instead of copying the entire library repeatedly. Compact snapshots do not build a nested tree only to discard it. Review selects eligible, due cards in authored order before loading required prompt content; calendar/statistics do not load all Markdown answers.
2. **Editing and search:** after a completed index build, unchanged Markdown can be reused only when its validated path and complete file signature still match. A title-only edit rereads no unchanged Markdown; a body edit rereads that file. Immutable trigram memberships are reused for unchanged documents. Every build recreates current metadata, references, scopes, and query caches. Tests compare incremental results with a fresh index, including moves, additions, deletions, concurrent edits, and invalid paths.
3. **Review inclusion:** changing only an entry's review preference keeps its search/reference index when exact write and coherence checks succeed. The client no longer refetches unchanged linked items and references for that preference change. Each measured entry toggle issues one PATCH.
4. **Frontend work:** stable callbacks and memoized library rendering avoid rebuilding the navigation tree for unrelated state changes. Closed dialogs skip constructing content. Tree updates preserve untouched branches.
5. **Git status:** one porcelain-v2 status command supplies the branch and ahead/behind counts as well as changed files. The ordinary path uses four subprocesses instead of seven. Results remain fresh; they are not cached. Tests include detached/unborn branches, missing upstreams, unusual filenames, and malformed records.
6. **Deletion:** items without candidate assets skip the survivor-asset content scan. Ordinary v2 deletion now moves only selected roots into durable transaction trash and proves the remaining tree unchanged by topology and signature checks. It updates trusted metadata without a full backup or full parse. Durable deleted-entry records persist until review cleanup is acknowledged; acknowledged trash is removed after the response. The frontend requests `include_library=false`, avoiding a full response that it previously discarded before requesting the compact bootstrap; the API default remains compatible.

Write journals, rollback, path validation, shared-asset guards, review cleanup, and deletion confirmations remain in place. Full backups remain for other structural writes. A cold or externally changed library still receives full validation before use. Search's bounded direct-file-change check remains 250 ms. Cache reuse does not change the storage format or redirect authored content into a database.

## Remaining limits and next priorities

1. **Other structural writes remain slow.** Initial API observations for creation, variants, namespace changes, moves, and reordering are generally 2.7–3.1 seconds. The complete library backup and full validation dominate. Deletion now has a narrower recoverable transaction; extending that design to writes that create or rebind references requires separate correctness work. Deletion still checks library-wide signatures and surviving asset references and refreshes the reader/search index afterward.
2. **Cold startup and payload size remain substantial.** One server startup measured 2.46 → 2.30 seconds; this is not a reliable distribution. Compact bootstrap still transfers 234,641 gzip bytes (1,372,408 decoded bytes). The first incoming-reference map still costs about 0.33 seconds. Slow networks and slower phones may amplify these costs.
3. **Already-fast actions are not uniformly faster.** Search, reference previews, and initial editor opening show little useful change. Some single API writes and after-idle measurements are slower in the final run. The main editing gain is reducing the work after the write, not making every disk write faster. Consult the complete tables and raw ranges before interpreting small differences.
4. **Coverage has boundaries.** The browser suite covers ordinary reading, navigation, search, previews, review, editing, dialogs, and confirmed deletion. The API suite additionally covers creation, variants, moves, ordering, media/drawing operations, PDF export, and synthetic login/logout. It does not time every possible diagram interaction, every keyboard shortcut, remote Git operations, real phone hardware, adverse network conditions, or sustained concurrent requests. The source copy had 17 reviewed entries and 23 log records in the deletion diagnosis; very long review histories were not stress-tested.

## Verification

- `python -m ruff check study.py study_app tests scripts/benchmark_performance.py scripts/benchmark_browser.py` — passed.
- `python -m pytest -ra` — **329 passed** in 24.02 seconds after scoped deletion; [output](performance/2026-09-14/scoped-deletion/python-tests.txt). The initial performance phase had 305 passing tests.
- `npm test` — **47 passed**; frontend lint and `npx tsc --noEmit` passed.
- `npm run build` — passed and staged the complete frontend under `study_app/web/`. The existing large-chunk warning remains; runtime assets are still served locally.
- `python study.py --check-data` — valid v2 data, 242 folders / 1,454 entries / 2,330 Markdown files. Benchmark copies also validated after mutation/cleanup.
- Browser comparison — 41 everyday desktop/phone action groups × 3 samples, plus 3 deletion groups × 3 samples, per version. No page errors or visible error messages; final runs also record HTTP errors in their JSON. Deletion checks verify missing deleted IDs and the correct remaining selection. Phone checks include drawer focus/Escape and overflow.
- A representative PDF export succeeded before and after. The final page was rendered and visually inspected: math, alternative formulation, and proof are legible with no clipping. [PDF render](performance/2026-09-14/pdf-export.png).
- Independently reviewed cache publication, rollback, shared-asset guards, incremental index equivalence, review order/eligibility, API compatibility, and frontend callback dependencies. No actionable findings remained.
- `git diff --check` passed; `git diff --name-only -- data` was empty. Authored content and review history remain unchanged.

The initial API and everyday browser after-runs below describe the first performance phase. The [scoped deletion follow-up](performance/2026-09-14/scoped-deletion/README.md) records subsequent tests and measurements against the completed source and rebuilt frontend, and supersedes the older deletion measurements.

## Files and reproducibility

The [exact changed-file manifest](performance/2026-09-14/changed-files.txt) includes source, tests, documentation, evidence, and generated frontend assets. Generated chunk filenames change together with their importers; the frontend dependencies were not upgraded.

Main implementation files:

- [`study_app/store.py`](../study_app/store.py): validated read views, flat snapshots, batch reads, signature scans, guarded content/index reuse, preference fast path, deletion and post-write cache retention.
- [`study_app/scoped_deletion.py`](../study_app/scoped_deletion.py): scoped deletion journals, safe filesystem moves, recovery, durable review acknowledgment, and deferred trash cleanup.
- [`study_app/search_index.py`](../study_app/search_index.py): incremental immutable posting reuse with fresh-build fallback.
- [`study_app/review.py`](../study_app/review.py): metadata-first queues, calendar, and statistics.
- [`study_app/app.py`](../study_app/app.py): compact snapshots and optional deletion-library response.
- [`study_app/git_ops.py`](../study_app/git_ops.py): fewer read-only status subprocesses.
- [`frontend/app/page.tsx`](../frontend/app/page.tsx), the export/Git/macros/move dialog components, [`frontend/lib/api.ts`](../frontend/lib/api.ts), and [`frontend/lib/library-tree.ts`](../frontend/lib/library-tree.ts): avoid repeated rendering and discarded requests/results.
- [`docs/SEARCH.md`](SEARCH.md) and [`docs/STORAGE.md`](STORAGE.md): current cache/coherence and transaction contracts.
- [`scripts/benchmark_performance.py`](../scripts/benchmark_performance.py) and [`scripts/benchmark_browser.py`](../scripts/benchmark_browser.py): repeatable measurements on temporary library copies.

Run from the development environment with backend/test dependencies, Playwright Chromium, and a built frontend. Use a separate frozen checkout of `8ce8622` for `BASELINE`, and the same unchanged Git root for both versions. The scripts copy data themselves and never perform Git mutations.

```sh
python scripts/benchmark_performance.py --source-root /path/to/BASELINE --git-root /path/to/BASELINE --samples 7 --pdf --output /tmp/api-before.json
python scripts/benchmark_performance.py --source-root /path/to/UPDATED --git-root /path/to/BASELINE --samples 7 --pdf --output /tmp/api-after.json
python scripts/benchmark_browser.py --source-root /path/to/BASELINE --git-root /path/to/BASELINE --samples 3 --output /tmp/browser-before.json
python scripts/benchmark_browser.py --source-root /path/to/UPDATED --git-root /path/to/BASELINE --samples 3 --output /tmp/browser-after.json
python scripts/benchmark_browser.py --source-root /path/to/BASELINE --git-root /path/to/BASELINE --samples 3 --focus deletion --output /tmp/deletion-before.json
python scripts/benchmark_browser.py --source-root /path/to/UPDATED --git-root /path/to/BASELINE --samples 3 --focus deletion --output /tmp/deletion-after.json
```

Run these sequentially, without concurrent tests/builds/benchmarks. Raw files record all measured values, not only improvements:

- [API before](performance/2026-09-14/api-before.json) / [API after](performance/2026-09-14/api-after.json).
- [Browser before](performance/2026-09-14/browser-before.json) / [Browser after](performance/2026-09-14/browser-after.json).
- [Deletion before](performance/2026-09-14/browser-deletion-before.json) / [Deletion after](performance/2026-09-14/browser-deletion-after.json).

Selected final visual checks: [desktop reader](performance/2026-09-14/desktop-1-reader-dark.png), [phone reader](performance/2026-09-14/phone-1-reader-dark.png), [phone review](performance/2026-09-14/phone-1-review.png), and [deletion result](performance/2026-09-14/deletion-result.png).

## Complete API timing table

All times are milliseconds. This historical table describes the first performance phase; consult the scoped follow-up's API run for the later implementation. “First” is the first request in that sequence after application setup, not necessarily a cold independent cache. API deletion rows retain the compatible full-library response; the entry has test assets and review history. The separate browser deletion rows use the frontend's lean response and assetless synthetic entries.

| API action | Samples before / after | Before median | After median |
|---|---:|---:|---:|
| `application_startup` | 1 / 1 | 2,455.64 | 2,302.45 |
| `session_first` | 1 / 1 | 2.44 | 1.68 |
| `session` | 7 / 7 | 0.77 | 0.79 |
| `bootstrap_compact_first` | 1 / 1 | 363.15 | 381.33 |
| `bootstrap_compact` | 7 / 7 | 192.81 | 130.26 |
| `bootstrap_compact_after_idle` | 5 / 5 | 214.19 | 159.49 |
| `bootstrap_full_first` | 1 / 1 | 259.53 | 159.92 |
| `bootstrap_full` | 7 / 7 | 205.59 | 162.48 |
| `entry_read_first` | 1 / 1 | 94.11 | 16.03 |
| `entry_read` | 7 / 7 | 32.70 | 13.80 |
| `entry_read_after_idle` | 5 / 5 | 56.05 | 35.18 |
| `linked_items_first` | 1 / 1 | 333.78 | 333.32 |
| `linked_items` | 7 / 7 | 0.99 | 0.89 |
| `linked_items_after_idle` | 5 / 5 | 31.59 | 36.20 |
| `search_first` | 1 / 1 | 2.77 | 2.89 |
| `search` | 7 / 7 | 1.45 | 1.40 |
| `search_after_idle` | 5 / 5 | 34.71 | 36.64 |
| `reference_first` | 1 / 1 | 2.03 | 1.87 |
| `reference` | 7 / 7 | 1.42 | 1.24 |
| `reference_batch_first` | 1 / 1 | 1.62 | 1.51 |
| `reference_batch` | 7 / 7 | 1.16 | 1.17 |
| `reference_picker_first` | 1 / 1 | 3.02 | 3.06 |
| `reference_picker` | 7 / 7 | 1.24 | 1.21 |
| `review_queue_first` | 1 / 1 | 161.11 | 36.61 |
| `review_queue` | 7 / 7 | 107.60 | 33.28 |
| `review_queue_after_idle` | 5 / 5 | 116.85 | 62.04 |
| `calendar_first` | 1 / 1 | 569.16 | 70.51 |
| `calendar` | 7 / 7 | 567.47 | 67.81 |
| `calendar_after_idle` | 5 / 5 | 561.89 | 90.34 |
| `git_status_first` | 1 / 1 | 205.06 | 156.89 |
| `git_status` | 7 / 7 | 130.09 | 72.48 |
| `drawing_templates_first` | 1 / 1 | 1.85 | 1.85 |
| `drawing_templates` | 7 / 7 | 0.93 | 0.83 |
| `folders_review_toggle` | 6 / 6 | 479.61 | 286.57 |
| `folders_search_after_toggle` | 1 / 1 | 1.69 | 1.67 |
| `folders_linked_items_after_toggle` | 1 / 1 | 1.12 | 1.04 |
| `entries_review_toggle` | 6 / 6 | 411.36 | 301.18 |
| `entries_search_after_toggle` | 1 / 1 | 1,456.90 | 1.63 |
| `entries_linked_items_after_toggle` | 1 / 1 | 4.59 | 1.02 |
| `folder_create` | 1 / 1 | 2,611.60 | 2,672.71 |
| `entry_create` | 1 / 1 | 3,734.92 | 2,700.39 |
| `entry_title_save` | 3 / 3 | 195.82 | 169.62 |
| `content_save` | 3 / 3 | 177.59 | 194.80 |
| `content_unchanged_save` | 3 / 3 | 33.78 | 31.50 |
| `search_after_save` | 1 / 1 | 1,324.76 | 303.56 |
| `linked_items_after_save` | 1 / 1 | 4.20 | 5.65 |
| `formulation_add` | 1 / 1 | 2,488.67 | 2,698.12 |
| `supplement_add` | 1 / 1 | 3,517.09 | 2,730.59 |
| `variant_promote` | 1 / 1 | 3,512.24 | 2,755.20 |
| `entry_tag_rename` | 1 / 1 | 3,508.00 | 2,729.02 |
| `folder_rename` | 1 / 1 | 3,569.32 | 2,795.69 |
| `entry_move` | 1 / 1 | 4,853.11 | 2,970.29 |
| `folder_move` | 1 / 1 | 3,781.45 | 2,927.05 |
| `entry_reorder` | 1 / 1 | 4,990.60 | 2,936.58 |
| `macros_save` | 1 / 1 | 2.37 | 2.36 |
| `image_upload` | 1 / 1 | 2,562.70 | 2,771.58 |
| `image_read` | 7 / 7 | 35.32 | 31.87 |
| `drawing_save` | 1 / 1 | 2,672.38 | 2,712.49 |
| `commutative_save` | 1 / 1 | 3,647.88 | 2,818.46 |
| `drawing_templates_save` | 1 / 1 | 2.45 | 2.05 |
| `review_reveal_0` | 1 / 1 | 128.22 | 50.99 |
| `review_grade_0` | 1 / 1 | 76.48 | 35.94 |
| `review_reveal_1` | 1 / 1 | 127.97 | 51.59 |
| `review_grade_1` | 1 / 1 | 75.26 | 36.23 |
| `review_reveal_2` | 1 / 1 | 128.19 | 50.10 |
| `review_grade_2` | 1 / 1 | 74.95 | 87.41 |
| `pdf_export` | 1 / 1 | 534.01 | 524.36 |
| `entry_delete` | 1 / 1 | 4,066.07 | 3,116.76 |
| `folder_delete` | 1 / 1 | 3,988.04 | 2,885.55 |
| `login_0` | 1 / 1 | 28.16 | 27.02 |
| `logout_0` | 1 / 1 | 2.14 | 2.50 |
| `login_1` | 1 / 1 | 26.83 | 26.29 |
| `logout_1` | 1 / 1 | 2.15 | 1.90 |
| `login_2` | 1 / 1 | 26.58 | 27.38 |
| `logout_2` | 1 / 1 | 1.80 | 1.88 |

## Complete browser timing table

All times are milliseconds; each row has three samples per version. This historical table describes the first performance phase. Later deletion results are in the scoped follow-up. The raw files include min/max and all three measurements.

| Browser action | Before median | After median |
|---|---:|---:|
| `desktop.cold_content_ready` | 388.28 | 305.66 |
| `desktop.cold_settled` | 536.18 | 435.13 |
| `desktop.warm_reload_settled` | 462.89 | 306.43 |
| `desktop.next_entry` | 80.55 | 65.23 |
| `desktop.previous_entry` | 80.24 | 54.53 |
| `desktop.search_results` | 189.07 | 184.92 |
| `desktop.search_typing_results` | 287.64 | 283.67 |
| `desktop.reference_preview` | 254.57 | 260.93 |
| `desktop.dark_theme` | 61.72 | 53.09 |
| `desktop.entry_review_toggle` | 528.34 | 397.18 |
| `desktop.folder_review_toggle` | 473.27 | 404.89 |
| `desktop.library_resize` | 29.49 | 13.84 |
| `desktop.library_hide` | 26.40 | 20.71 |
| `desktop.library_expand_collapse` | 25.11 | 22.24 |
| `desktop.calendar_open` | 901.47 | 436.51 |
| `desktop.calendar_next_month` | 548.61 | 86.19 |
| `desktop.review_open` | 458.36 | 388.26 |
| `desktop.review_reveal_synthetic` | 207.83 | 83.45 |
| `desktop.review_grade_synthetic` | 275.69 | 101.57 |
| `desktop.editor_open` | 345.88 | 340.31 |
| `desktop.editor_title_save` | 2,010.96 | 828.27 |
| `desktop.editor_reopen` | 33.26 | 26.84 |
| `desktop.editor_body_save` | 2,030.71 | 795.36 |
| `desktop.editor_unchanged_save` | 268.17 | 266.55 |
| `desktop.dialogs_reopen` | 1,954.77 | 1,922.54 |
| `phone.cold_content_ready` | 369.83 | 275.92 |
| `phone.cold_settled` | 521.57 | 420.43 |
| `phone.warm_reload_settled` | 462.61 | 283.70 |
| `phone.next_entry` | 77.48 | 56.46 |
| `phone.previous_entry` | 74.46 | 53.22 |
| `phone.search_results` | 184.22 | 184.04 |
| `phone.search_typing_results` | 282.21 | 279.85 |
| `phone.reference_preview` | 70.76 | 68.72 |
| `phone.dark_theme` | 86.34 | 83.10 |
| `phone.entry_review_toggle` | 513.44 | 333.20 |
| `phone.library_drawer` | 26.86 | 31.27 |
| `phone.calendar_open` | 912.96 | 454.49 |
| `phone.calendar_next_month` | 565.24 | 74.28 |
| `phone.review_open` | 546.41 | 406.17 |
| `phone.review_reveal_synthetic` | 141.12 | 80.68 |
| `phone.review_grade_synthetic` | 292.71 | 110.35 |
| `desktop.delete_entry` | 6,159.37 | 3,386.68 |
| `desktop.delete_empty_folder` | 6,224.75 | 3,447.36 |
| `desktop.delete_folder_subtree` | 6,111.59 | 3,447.88 |
