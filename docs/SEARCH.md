# Search and `@tag` references

Study treats a short reference as a lexical name, not as a globally unique identifier. Given a
folder and `@group`, resolution checks deterministic stages: direct current folder, current
descendants, direct parent, the sibling subtrees newly visible there, then the same direct/subtree
pair at each higher ancestor. If the originating top-level tree has no match, one final global stage
checks all other top-level trees. The first nonempty stage shadows every farther stage, so a local or
higher-level target cannot become ambiguous merely because the same short tag exists globally.

Entries of different kinds may intentionally share a raw tag in one folder because their canonical
tags remain distinct. A short reference to that raw tag is **ambiguous**; Study reports every match
at that stage and does not guess or continue outward. A fully qualified canonical tag such as
`@math:algebra:df:group` resolves exactly and is the safe insertion offered for an ambiguous match.
Resolved references render as the entry title without rewriting the authored `@tag`. The labeled
form `@[replacement text]tag` resolves exactly the same tag while using the replacement text inline;
its preview heading remains the resolved entry title. The replacement must be nonempty, single-line
plain text without square brackets. Missing and ambiguous references remain as their complete
authored source text, including the label when present.

Alternative formulations and supplements are addressable in the same way:

```text
@group:category
@lagrange:pf
@lagrange:pf:action
```

Resolution is read-only. The backend does not rewrite Markdown, so searching or resolving cannot
alter `@` characters inside prose, code, or mathematics.

## Read API

- `GET /api/search?q=...&limit=40&folder_id=...` searches titles, tags, headers, formulations,
  proofs, and solutions. `folder_id` is optional and improves contextual ranking.
- `GET /api/references/resolve?folder_id=...&tag=@group` returns `resolved`, `missing`, or
  `ambiguous`. A resolved response includes the selected variant, entry header, and main
  formulation Markdown for hover preview. A global fallback reports `resolution: "global"` and
  leaves `matched_folder_id` and `scope_distance` null because it has no single ancestor scope.
- `GET /api/references/resolve-batch?folder_id=...&tag=@group&tag=@field` resolves
  1–100 tags against one snapshot and returns `{revision, results: [{tag, result}]}` in
  input order. Each `result` has the single-resolution shape. Individual tags retain the
  8,192-character limit; a batch is bounded at 65,536 tag characters. The reader groups
  simultaneous same-folder requests and deduplicates requests already in flight. It does
  not retain completed results across page visits, so client caches cannot mask disk edits.
- `GET /api/entries/{entry_id}/linked-items?offset=0&limit=40` returns incoming references
  from headers, formulations, alternative formulations, proofs, and solutions. The response
  contains `entry_id`, `revision`, `total`, `offset`, `limit`, `next_offset`, and `items`.
  Entries appear once in authored order, including self-references when explicitly authored.
  Each item includes its source entry ID/title/kind, folder ID/namespace, and the canonical tag
  and variant ID of its first referencing location. A header location links to the main
  formulation and has a null variant ID. `reference_count` counts distinct source locations,
  not repeated mentions. Links to any target formulation or supplement count as links to the
  owning entry. Clients must reset pagination when the returned snapshot revision changes.
- `GET /api/references/candidates?folder_id=...&q=...&limit=40` returns targets selected by the same
  local-to-global precedence for the insertion picker. The UI inserts the returned `insert_text`
  verbatim.

All of these endpoints require the normal Study session (with local-mode bypass applying only to a
loopback client). Limits are bounded at 200 results. Folder depth is capped at 64 and exact
reference input at 8,192 characters, so every valid canonical tag fits without accepting an
unbounded URL parameter.

## Index design and coherence

`LibrarySearchIndex` is an immutable in-memory snapshot containing:

- folder-ID, ancestor-chain, preorder-rank, root, and subtree-interval maps;
- `(folder_id, local_reference)` and exact-canonical-tag hash maps;
- local-reference target rows sorted by folder preorder rank for binary-searched subtree ranges;
- normalized entry and variant documents, including normalized ranking fields;
- trigram-to-document inverted indexes for full-content and insertion search;
- an incoming-reference map, built lazily on the first linked-items request for that snapshot.

The incoming map parses Markdown prose tokens rather than searching for `@` with a whole-file
regular expression. It recognizes labeled references and excludes code, mathematics (both dollar
and slash delimiters), Markdown links, autolinks, HTML nodes, image alt text, emails, and escaped or
entity-encoded reference syntax. GFM tables and strikethrough are prose. The parser uses the same
literal-tag boundary rules as the reader. Only uniquely resolved targets form edges: missing,
ambiguous, and shadowed farther matches do not produce guessed links. The source-text parse cache
holds at most 8,192 documents across snapshots; its keys are exact content, so edits cannot reuse
stale parsing. Lexical resolution is recomputed for every new snapshot.

After the first incoming-map build, linked-items queries retrieve one precomputed list and copy
only the requested page. They do not scan Markdown or resolve the whole library on every page view.
Batch resolution checks disk coherence once for the entire batch rather than once per tag. Both
responses carry the opaque revision of the snapshot used; replacing a snapshot changes its revision.

A query intersects the smallest trigram posting lists first, then verifies the complete normalized
substring before ranking results. This verification prevents n-gram false positives. Ranking is
deterministic: exact canonical tag, exact raw tag, exact title, raw-tag prefix, title prefix,
canonical-tag prefix, metadata hit, then body hit. Within a category, ties are ordered by earliest
normalized occurrence, contextual scope precedence, authored order, then canonical tag.

The index keeps bounded least-recently-used caches: 512 ranked library queries, 512 ranked visible
reference queries, and 8,192 resolved `(origin-folder, local-reference)` groups. Visible groups are
built lazily rather than materializing a folder-by-target matrix. The result limit is intentionally
absent from ranking cache keys, so one ordering serves different limits. Replacing the immutable
snapshot after a write or pull drops every cached result atomically.

Exact canonical and direct-scope lookups use hash maps; subtree and global stages use binary searches
over preorder-ranked target rows. Short-name resolution is therefore proportional to folder depth
and the matches in the first nonempty stage, not library size. Full-text query cost is proportional
to the smallest intersected posting lists plus verified matches. Very common terms can still
approach a full scan; the result cap bounds response size, not that honest worst case.

Markdown files are read once for the first snapshot, not once per query. Later v2 builds reuse
unchanged Markdown strings from the previous completed build only when both their validated
absolute paths and five-part file signatures match the complete pre-build tree scan. New or
changed files go through the normal guarded reads. Full library/tree signatures must still match
before and after loading, and only successful index construction publishes the replacement content
cache, pruning removed paths. This cache contains at most the Markdown paths in one completed
library snapshot; v1 builds retain full reads and clear it. A metadata-only edit therefore rereads
no unchanged Markdown, while an edit to one body rereads that file. Every rebuild still creates new
metadata, ranking, scope-resolution, and incoming-reference indexes so title, namespace, and link
changes cannot inherit old results.

The previous completed index may supply immutable trigram posting memberships for the new build.
Only documents whose normalized searchable text changed, including added or removed document keys,
require membership updates; unchanged posting sets are shared. The new index still constructs its
current titles, tags, authored order, targets, and lexical scopes, starts with empty query caches,
and builds its own incoming links lazily. It retains no predecessor link. The store keeps only the
last completed index for this reuse, and never serves that retained index after invalidation.
For broad replacements, the builder compares the amount of old/new text that would need
retokenizing with a fresh build and chooses the smaller estimated workload.

Every store write that can affect indexed content, canonical tags, lexical scope, or ranking
invalidates the snapshot immediately. The v2 exceptions are updates containing only a non-null folder or entry
`review_enabled` preference, which search does not consume. Study preserves the existing search
snapshot and revision after those atomic single-sidecar writes only if the index matched disk
beforehand and the validated library-cache refresh finds no unexpected concurrent change;
otherwise it invalidates the snapshot normally. Entry preferences retain the same recovery journal
and rollback checks as other entry edits.

Ordinary v2 entry edits retain the validated library cache only after checking the exact saved
bytes and confirming that all other file signatures are unchanged. Content and other metadata edits
still invalidate the search snapshot immediately. The editor sends only changed fields and
variants and defers mounted-reader refresh until all requests in that save have settled, including
partially successful saves. This prevents reference and linked-item reads from repeatedly rebuilding
the index between writes. Unchanged saves issue no writes or reader invalidations.

Cross-folder entry moves in the interactive app
validate the relocated entry and verify moved-file signatures, exact saved metadata, directory
identity, and unchanged neighbors before retaining the cache. Unexpected disk changes force a
complete parse. Moves invalidate search immediately, while the frontend batches reader refreshes
until the library and selected entry are updated. Navigation-only bootstrap responses omit headers,
asset records, and variant file paths; entry-detail and legacy bootstrap responses remain complete.

Snapshot, entry, and search-index reads inspect the validated metadata without copying the whole
library before copying their returned entries. Compact bootstrap and review snapshots omit the derived
tree, and batched entry reads validate once before loading only the selected entries. The public
results remain independent copies; writes use their own mutable metadata copy. Ordinary metadata
and entry reads still check disk signatures on every operation. Signature walks use directory
entries to avoid redundant file-type checks while retaining every file and directory signature,
symlink rejection during validation, and before/after checks around index construction.

A successful app-controlled Git pull synchronously reloads the index. To catch direct on-disk
edits, Study checks `library.json` on every query and performs a signature sweep at most once every
250 milliseconds. For aggregate v1 storage this covers the indexed Markdown paths. For sharded v2
storage it also covers folder/entry sidecars and the traversed directories, so additions, deletions,
and slug-derived directory moves invalidate the snapshot. The signature includes device, inode,
size, modification time, and change time. Thus a valid manual edit may remain visible through the
old cache for at most 250 milliseconds and is refreshed on the next query after that bound.
