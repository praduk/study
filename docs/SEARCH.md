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
- `GET /api/references/candidates?folder_id=...&q=...&limit=40` returns targets selected by the same
  local-to-global precedence for the insertion picker. The UI inserts the returned `insert_text`
  verbatim.

All three endpoints require the normal Study session (with local-mode bypass applying only to a
loopback client). Limits are bounded at 200 results. Folder depth is capped at 64 and exact
reference input at 8,192 characters, so every valid canonical tag fits without accepting an
unbounded URL parameter.

## Index design and coherence

`LibrarySearchIndex` is an immutable in-memory snapshot containing:

- folder-ID, ancestor-chain, preorder-rank, root, and subtree-interval maps;
- `(folder_id, local_reference)` and exact-canonical-tag hash maps;
- local-reference target rows sorted by folder preorder rank for binary-searched subtree ranges;
- normalized entry and variant documents, including normalized ranking fields;
- trigram-to-document inverted indexes for full-content and insertion search.

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

Markdown files are read once when a snapshot is built, not once per query. Every normal store write
invalidates the snapshot immediately. A successful app-controlled Git pull synchronously reloads
it. To catch direct on-disk edits, Study checks `library.json` on every query and performs a
signature sweep at most once every 250 milliseconds. For aggregate v1 storage this covers the
indexed Markdown paths. For sharded v2 storage it also covers folder/entry sidecars and the
traversed directories, so additions, deletions, and slug-derived directory moves invalidate the
snapshot. The signature includes device, inode, size, modification time, and change time. Thus a
valid manual edit may remain visible through the old cache for at most 250 milliseconds and is
refreshed on the next query after that bound.
