# Structural write performance on the production host

The interactive v2 writer now creates entries/folders and renames/moves folders without
revalidating and reparsing unrelated authored files. It writes only changed metadata and new
content, moves ordinary folder directories as a unit, and retains the validated snapshot only
when complete file signatures account for every change. Search is invalidated normally. External
edits cause full validation. Deep-folder storage layout transitions and stores with recovery
backups enabled retain the general writer.

Profiling on the production Python 3.12 runtime also identified repeated `Path.relative_to`
ancestor construction. Component-prefix comparisons now perform the equivalent lexical check;
symlink and disk containment protections remain in the validator and guarded file accesses.

## Production-host comparison

Sequential before/after runs on `pradu.us`, using the deployed baseline backend and the candidate
backend against disposable copies of the same-sized library: 250 folders, 1,542 entries, 2,471
Markdown files. The benchmark uses HTTP on a temporary loopback port, gzip, and three samples per
operation. Both folder rename and folder move operate on a populated folder. Source authored data
and review history are not changed. The live service remains running during measurement, so host
load can contribute variation. Results exclude internet latency and browser rendering.

| Operation | Before median | After median | Reduction |
| --- | ---: | ---: | ---: |
| Create folder | 6,018.86 ms | 598.92 ms | 90.0% |
| Create entry | 5,941.91 ms | 600.19 ms | 89.9% |
| Rename populated folder | 5,743.57 ms | 585.86 ms | 89.8% |
| Move populated folder | 6,427.76 ms | 615.53 ms | 90.4% |

Entry moves remained about 0.55 seconds. Navigation refresh after an entry move remained about
0.20 seconds median, with a first refresh around 1.1 seconds. Full samples are in `before.json` and
`after.json`. These are small-sample observations, not latency guarantees; large subtrees, outside
edits, and deep-layout fallback can cost more.

## Validation and deployment

- 349 Python tests and 51 frontend tests passed; Python/frontend lint, TypeScript, and frontend
  production build passed. Authored-library validation and `git diff --check` passed.
- Nine focused tests exercise creation, folder reorder/move/rename, sparse-rank exhaustion,
  external changes during all four operations, duplicate ID rejection, deep-layout fallback,
  asset preservation, stable IDs/inodes, fresh canonical references, and reopen persistence.
- In-app browser verified entry creation, populated-folder movement, updated canonical URL/tree,
  and persistence after reload using a disposable fixture. Folder creation/rename HTTP endpoints
  were exercised by the production-host benchmark; the in-app browser did not expose their native
  prompt dialogs for automation.
- Installed the verified backend `study_app/store.py` directly on production, without a Git commit,
  push, or pull. Previous backend retained at
  `/home/pradu/study-code-backups/20260918T092915Z-structural-writes/store.py`.
- All 4,272 authored data files were byte-identical across installation. Production library
  validation passed, service startup completed, public health returned OK, and session inspection
  confirmed server authentication remains required. Local service was also restarted.

Changed files: `study_app/store.py`, `tests/test_structural_writes.py`,
`scripts/benchmark_structural_writes.py`, `README.md`, `docs/SEARCH.md`, and this directory's
`README.md`, `before.json`, and `after.json`. No frontend source or generated assets changed.

Reproduce with the server's Python environment:

```sh
python scripts/benchmark_structural_writes.py --source-root /path/to/code --data-root /path/to/data --output /tmp/structural-writes.json
```
