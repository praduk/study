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

Study's search index watches v2 sidecars, Markdown files, and the relevant directory signatures.
A valid direct edit becomes visible on the next query after the bounded 250 ms staleness check.
Normal v2 mutations use a prepared/committed recovery journal. If startup must displace an
interrupted live tree, it retains that tree under ignored `data/runtime/` storage so a manual edit
made while Study was stopped is not silently deleted.
