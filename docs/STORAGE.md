# Authored storage formats

Study supports two on-disk formats while exposing the same normalized folders, entries, variants,
and ordering through `LibraryStore` and the HTTP API.

## Version 1: aggregate metadata

Version 1 stores folder and entry metadata in `data/library.json`. Markdown is already split into
`data/content/<entry-id>/<variant-id>.md`. This format remains fully readable and writable; opening
an existing library never migrates it. Brand-new data roots initialize as version 2.

## Version 2: sharded metadata and colocated Markdown

In version 2, `data/library.json` is only this format marker:

```json
{
  "version": 2,
  "root": "library"
}
```

The authored tree is derived from folder slugs and entry kind/tag components:

```text
data/library/
  _library.json
  math/
    _folder.json
    algebra/
      _folder.json
      _items/
        df/
          group/
            _entry.json
            formulation.<stable-variant-id>.md
        th/
          lagrange/
            _entry.json
            formulation.<stable-variant-id>.md
            proof.<stable-variant-id>.md
```

The small `_library.json` root sentinel keeps an intentionally empty v2 library representable in
Git and distinguishes it from a missing tree.

Folder sidecars store the stable folder ID, display name, review setting, timestamps when present,
and a sparse `rank`. The directory name supplies `slug`, and nesting supplies `parent_id`.

Entry sidecars store the stable entry ID, title, header, problem metadata, variants, assets,
timestamps when present, and a sparse `rank`. The path supplies `folder_id`, `kind`, and `tag`.
Variant `file` values in a sidecar are single Markdown basenames; `LibraryStore` expands them to the
same data-relative paths used by the existing API. Derived canonical tags and review modes are not
duplicated on disk.

Stable IDs do not change when a folder or entry is renamed or moved. The corresponding directory
moves because paths are meant to be human-readable and Git-reviewable. Sparse ranks preserve
authored order without rewriting every peer sidecar for a typical insertion or move; the API still
returns zero-based `order` values.

Literal nested slug paths are used for ordinary trees. If the worst-case entry path below a folder
would exceed the conservative portable path budget, that folder is represented under
`data/library/_deep/<32-hex-namespace-hash>-<leaf-slug>/`. Its sidecar retains the logical slug and
parent ID. Each deeper descendant is independently represented there. Study recomputes the hash
from the complete logical namespace and rejects collisions or noncanonical placement. This escape
hatch preserves the 64-level namespace limit without relying on filesystem-specific long paths.

Shared `macros.json`, review state/history, media, diagram sources, exports, and runtime state stay
at their existing global `data/` paths. Only library metadata and Markdown are sharded.

JSON sidecars are intentional. Python's standard library reads and writes them, their types are
unambiguous, and no YAML or front-matter parser is required. Markdown files contain only authored
Markdown.

## Validation and direct edits

Both normal startup and candidate Git pulls validate the selected format before using it. Version 2
fails closed for:

- missing or malformed sidecars and referenced Markdown;
- duplicate stable IDs, duplicate sibling slugs, or duplicate per-kind entry tags;
- unknown files or directories in the authored tree;
- symbolic links anywhere below `data/library/`;
- invalid kinds, slug-derived paths, excessive nesting or path length, and escaping paths;
- incompatible formulations, proofs, solutions, assets, or review modes.

Direct edits are supported, but the directory path is authoritative for slugs, kinds, and tags.
Move the whole entry directory when changing one of those values. Keep stable IDs unchanged. Run:

```sh
python study.py --check-data
```

Study's search index watches v2 sidecars, Markdown files, and the relevant directory signatures.
A valid direct edit becomes visible on the next query after the bounded 250 ms staleness check.
Normal v2 mutations use a prepared/committed recovery journal. If startup must displace an
interrupted live tree, it retains that tree under ignored `data/runtime/` storage so a manual edit
made while Study was stopped is not silently deleted.

## Explicit migration

Commit or otherwise clear all local changes, validate the source, and then migrate:

```sh
python study.py --check-data
python study.py --migrate-storage
python study.py --check-data
git diff --stat
git diff -- data/library.json data/library
```

The migration command refuses a non-Git directory, an in-progress Git operation, a dirty worktree,
an existing v2 tree, an invalid v1 library, unknown top-level library metadata, non-UTF-8 Markdown,
or unreferenced/unsafe files under `data/content/`. It stages a complete v2 tree under the protected
runtime directory, hashes and compares every normalized record and Markdown body, then replaces the
aggregate file with the tiny marker. Compatible running Study processes share an interprocess data
lock. Before freezing the v1 source, migration durably records a prepared journal; startup restores
v1 after an interrupted prepared cutover or retains a validated v2 tree after a committed cutover.
If recovery cannot prove that a competing path is disposable, it preserves that path inert under
`data/runtime/` rather than deleting it. It does not alter `review.json`, `review-log.jsonl`, global
macros, media, or diagrams. The old `data/content/` paths become Git deletions and the colocated
files become additions; Git can usually recognize those identical bodies as renames when presenting
the diff.

Migration is one-way in the application. Use the surrounding Git commit to inspect, share, or roll
back the format transition. Do not mix v1 aggregate records with a v2 marker.
