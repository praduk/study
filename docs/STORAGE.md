# Authored storage formats

Study supports two on-disk formats while exposing the same normalized folders, entries, variants,
and ordering through `LibraryStore` and the HTTP API.

## Version 1: aggregate metadata

Version 1 stores folder and entry metadata in `data/library.json`. Markdown is already split into
`data/content/<entry-id>/<variant-id>.md`. This format remains fully readable and writable; opening
an existing library does not change its format. Brand-new data roots initialize as version 2.

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
            assets/
              <content-hash>.png
        th/
          lagrange/
            _entry.json
            formulation.<stable-variant-id>.md
            proof.<stable-variant-id>.md
            assets/
              <stable-asset-id>.excalidraw
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

Entry-owned image previews and editable Excalidraw or commutative-diagram sources live one level
below that same entry in `assets/`. Their sidecar paths are entry-local, while the stable public
Markdown syntax is independent of the entry's current slug path. Moving or renaming an entry moves
its Markdown and assets together. The shared Excalidraw library and templates remain global because
they are not owned by one entry.

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

Shared `macros.json`, review state/history, the Excalidraw template library, exports, and runtime
state stay at their existing global `data/` paths. Version 1 keeps its legacy global media and
diagram paths; new version 2 assets are colocated with their owning entries.

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

After a complete version 2 parse and validation, `LibraryStore` keeps a deep-copied normalized
metadata snapshot in memory. It reuses that snapshot only after checking the recorded signatures of
`library.json`, every traversed directory, sidecar, Markdown file, and asset. A changed or missing
signature forces another complete parse and validation. Study also compares signatures from before
and after an uncached load, so a tree that changes while it is being read is never admitted to the
cache. Version 1 retains its existing uncached validation behavior.

Most structural writes keep a complete independent backup and prepared/committed recovery journal.
Their final validation reads the finished tree between full signature sweeps and retains that
validated snapshot. Rollback discards the newly validated cache before restoring normal reads.

Version 2 deletion instead uses a scoped, durable transaction. Starting from a trusted metadata
snapshot, Study checks every recorded disk signature, applies the deletion to an independent copy,
and moves only the minimal deleted entry/folder directories into transaction trash. Logical
subtrees that use `_deep` may require several independent physical moves. Surviving sidecars keep
their exact bytes and sparse ranks. Exclusive legacy assets outside the library tree are staged
individually; shared asset and surviving-Markdown guards still apply. When there are no candidate
assets, deletion skips scanning unrelated Markdown bodies.

Before committing, Study compares the complete surviving tree topology and signatures and checks
all detached files against their original signatures. Only the expected parent-directory changes
and detached roots' rename timestamps may differ. An unexpected direct edit aborts the deletion;
rollback restores detached directories and preserves conflicting new live paths under the
transaction's `conflicts/` directory. Unsafe or ambiguous recovery fails closed and retains its
recovery material. Normal unchanged deletion does not copy or reparse/validate the whole library.
Its cache contains the independently transformed metadata and the signatures proved by these
checks; edits after that proof still invalidate the next read.

Each transaction lives under `data/runtime/library-delete-<id>.tmp/`. Its prepared journal is
published durably before any authored directory moves. Startup rolls back prepared transactions;
committed transactions never resurrect deleted entries. Committed journals retain exact deleted
entry IDs until the review engine has purged their schedules, pending attempts, and history,
including when the same entry ID was restored through an external edit before that purge. Review
file renames are synced before the journal is durably marked `review-complete`. Only then may
background cleanup remove the trash. Multiple committed deletions can await this acknowledgement.
Acknowledged or successfully rolled-back directories are renamed out of the active journal
namespace before recursive cleanup, so interrupted cleanup cannot invalidate a live library.
Preparatory directories left before journal publication and conflicted rollbacks remain inert in
runtime storage for inspection. Unfinished transactions from the older full-library/entry-write
protocols block a new scoped deletion until recovery. Version 1 retains its original deletion path.

Study's search index watches v2 sidecars, Markdown files, and the relevant directory signatures.
A valid direct edit becomes visible on the next query after the bounded 250 ms staleness check.
Structural and content-changing v2 mutations use a prepared/committed recovery journal. The narrow
exception is a folder update whose only field is a non-null `review_enabled`: that preference has no path,
namespace, ordering, or indexed-content effect, so Study atomically replaces only the affected
folder's `_folder.json`. Before replacing it, Study verifies that the sidecar still matches the
signature used to build the current snapshot; a concurrent direct edit aborts the preference write
instead of being overwritten. Study retains the validated metadata cache only when every other
recorded signature is unchanged; otherwise the next read performs full validation. If startup must
displace an interrupted live tree, it retains that tree under ignored `data/runtime/` storage so a
manual edit made while Study was stopped is not silently deleted.
