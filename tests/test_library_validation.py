from __future__ import annotations

import io
import json
from pathlib import Path

import pytest
from PIL import Image
from pydantic import ValidationError

from study_app.models import FolderUpdate
from study_app.store import LibraryStore, StoreError


def _library(store: LibraryStore) -> dict:
    return json.loads(store.library_path.read_text(encoding="utf-8"))


def _write_library(store: LibraryStore, value: dict) -> None:
    store.library_path.write_text(json.dumps(value), encoding="utf-8")


def _store_with_entry(root: Path) -> tuple[LibraryStore, dict]:
    store = LibraryStore(root / "data")
    folder = store.create_folder("Geometry", "geometry", None)
    entry = store.create_entry(folder["id"], "df", "Object", "object", "", "Body")
    return store, entry


def _png_bytes(width: int = 4, height: int = 3) -> bytes:
    output = io.BytesIO()
    Image.new("RGB", (width, height), (20, 40, 60)).save(output, format="PNG")
    return output.getvalue()


def _append_asset(store: LibraryStore, entry_id: str, asset: dict) -> None:
    library = _library(store)
    entry = next(item for item in library["entries"] if item["id"] == entry_id)
    entry["assets"].append(asset)
    _write_library(store, library)


def test_folder_update_omits_slug_but_rejects_explicit_null() -> None:
    assert FolderUpdate.model_validate({}).model_dump(exclude_unset=True) == {}
    with pytest.raises(ValidationError, match="folder slug cannot be null"):
        FolderUpdate.model_validate({"slug": None})


def test_missing_markdown_is_rejected_instead_of_becoming_empty_content(tmp_path: Path):
    store = LibraryStore(tmp_path / "data")
    folder = store.create_folder("Algebra", "algebra", None)
    entry = store.create_entry(folder["id"], "df", "Group", "group", "", "Body")
    (store.data_dir / entry["formulations"][0]["file"]).unlink()

    with pytest.raises(StoreError, match="missing"):
        store.get_entry(entry["id"])


@pytest.mark.parametrize("corruption", ["missing-parent", "cycle", "duplicate-sibling"])
def test_invalid_folder_graph_is_rejected(tmp_path: Path, corruption: str):
    store = LibraryStore(tmp_path / "data")
    first = store.create_folder("First", "first", None)
    second = store.create_folder("Second", "second", first["id"])
    library = _library(store)
    folders = {folder["id"]: folder for folder in library["folders"]}
    if corruption == "missing-parent":
        folders[first["id"]]["parent_id"] = "does-not-exist"
    elif corruption == "cycle":
        folders[first["id"]]["parent_id"] = second["id"]
    else:
        folders[second["id"]]["parent_id"] = None
        folders[second["id"]]["slug"] = folders[first["id"]]["slug"]
    _write_library(store, library)

    with pytest.raises(StoreError):
        store.snapshot()


def test_folder_nesting_is_bounded_before_recursive_consumers(tmp_path: Path):
    store = LibraryStore(tmp_path / "data")
    parent_id = None
    for index in range(64):
        folder = store.create_folder(f"Level {index}", f"level-{index}", parent_id)
        parent_id = folder["id"]

    with pytest.raises(StoreError, match="cannot exceed 64 levels"):
        store.create_folder("Too deep", "too-deep", parent_id)
    assert len(store.snapshot()["folders"]) == 64


def test_duplicate_tags_and_invalid_main_formulations_are_rejected(tmp_path: Path):
    store = LibraryStore(tmp_path / "data")
    folder = store.create_folder("Algebra", "algebra", None)
    first = store.create_entry(folder["id"], "df", "Group", "group", "", "Body")
    second = store.create_entry(folder["id"], "df", "Ring", "ring", "", "Body")
    library = _library(store)
    entries = {entry["id"]: entry for entry in library["entries"]}
    entries[second["id"]]["tag"] = entries[first["id"]]["tag"]
    _write_library(store, library)

    with pytest.raises(StoreError, match="entry tags"):
        store.snapshot()

    entries[second["id"]]["tag"] = "ring"
    entries[first["id"]]["formulations"][0]["main"] = False
    entries[first["id"]]["formulations"][0]["subtag"] = "alternate"
    _write_library(store, library)
    with pytest.raises(StoreError, match="exactly one main"):
        store.snapshot()


def test_invalid_review_mode_dependency_is_rejected(tmp_path: Path):
    store = LibraryStore(tmp_path / "data")
    folder = store.create_folder("Algebra", "algebra", None)
    theorem = store.create_entry(folder["id"], "th", "Result", "result", "", "Body")
    library = _library(store)
    library["entries"][0]["review_modes"] = ["statement", "proof-plan"]
    _write_library(store, library)

    with pytest.raises(StoreError, match="requires a main proof"):
        store.get_entry(theorem["id"])


def test_valid_image_and_diagram_asset_records_are_accepted(tmp_path: Path):
    store, entry = _store_with_entry(tmp_path)
    preview_name = f"{'a' * 64}.png"
    (store.media_dir / preview_name).write_bytes(_png_bytes())

    store.register_asset(
        entry["id"],
        {
            "id": "image-asset",
            "kind": "image",
            "path": f"media/{preview_name}",
            "alt": "A valid image",
            "width": 70,
            "invert_lightness": False,
            "pixels": [4, 3],
        },
    )

    excalidraw_id = "b" * 32
    (store.diagram_dir / f"{excalidraw_id}.excalidraw").write_text(
        json.dumps({"type": "excalidraw", "version": 2, "elements": []}),
        encoding="utf-8",
    )
    store.register_asset(
        entry["id"],
        {
            "id": excalidraw_id,
            "kind": "excalidraw",
            "source": f"diagrams/{excalidraw_id}.excalidraw",
            "path": f"media/{preview_name}",
            "alt": "A valid drawing",
            "width": 76,
            "invert_lightness": True,
            "pixels": [4, 3],
        },
    )

    commutative_id = "c" * 32
    (store.diagram_dir / f"{commutative_id}.commutative.json").write_text(
        json.dumps(
            {
                "version": 1,
                "name": "A valid diagram",
                "width": 61,
                "nodes": [{"id": "a", "label": "$A$", "row": 0, "column": 0}],
                "arrows": [],
            }
        ),
        encoding="utf-8",
    )
    store.register_asset(
        entry["id"],
        {
            "id": commutative_id,
            "kind": "commutative",
            "source": f"diagrams/{commutative_id}.commutative.json",
            "alt": "A valid diagram",
            "width": 61,
        },
    )

    assert len(store.get_entry(entry["id"])["assets"]) == 3


def test_asset_paths_must_be_reachable_through_serving_routes(tmp_path: Path):
    store, entry = _store_with_entry(tmp_path)
    (store.media_dir / "friendly.png").write_bytes(_png_bytes())
    _append_asset(
        store,
        entry["id"],
        {
            "id": "unreachable-image",
            "kind": "image",
            "path": "media/friendly.png",
            "alt": "Unreachable image",
            "width": 70,
        },
    )

    with pytest.raises(StoreError, match="not reachable through a Study asset route"):
        store.snapshot()


def test_image_asset_contents_and_pixel_metadata_are_validated(tmp_path: Path):
    malformed_store, malformed_entry = _store_with_entry(tmp_path / "malformed")
    malformed_name = f"{'d' * 64}.png"
    (malformed_store.media_dir / malformed_name).write_bytes(b"not an image")
    _append_asset(
        malformed_store,
        malformed_entry["id"],
        {
            "id": "malformed-image",
            "kind": "image",
            "path": f"media/{malformed_name}",
            "alt": "Malformed image",
            "width": 70,
        },
    )
    with pytest.raises(StoreError, match="not a valid image"):
        malformed_store.snapshot()

    metadata_store, metadata_entry = _store_with_entry(tmp_path / "metadata")
    metadata_name = f"{'e' * 64}.png"
    (metadata_store.media_dir / metadata_name).write_bytes(_png_bytes())
    _append_asset(
        metadata_store,
        metadata_entry["id"],
        {
            "id": "wrong-pixels",
            "kind": "image",
            "path": f"media/{metadata_name}",
            "alt": "Wrong dimensions",
            "width": 70,
            "pixels": [5, 3],
        },
    )
    with pytest.raises(StoreError, match="pixel metadata does not match"):
        metadata_store.snapshot()


def test_diagram_asset_source_structure_is_validated(tmp_path: Path):
    excalidraw_store, excalidraw_entry = _store_with_entry(tmp_path / "excalidraw")
    preview_name = f"{'f' * 64}.png"
    (excalidraw_store.media_dir / preview_name).write_bytes(_png_bytes())
    excalidraw_id = "1" * 32
    (excalidraw_store.diagram_dir / f"{excalidraw_id}.excalidraw").write_text(
        json.dumps({"elements": {}}), encoding="utf-8"
    )
    _append_asset(
        excalidraw_store,
        excalidraw_entry["id"],
        {
            "id": excalidraw_id,
            "kind": "excalidraw",
            "source": f"diagrams/{excalidraw_id}.excalidraw",
            "path": f"media/{preview_name}",
            "alt": "Malformed drawing",
            "width": 70,
        },
    )
    with pytest.raises(StoreError, match="Excalidraw elements must be a list"):
        excalidraw_store.snapshot()

    commutative_store, commutative_entry = _store_with_entry(tmp_path / "commutative")
    commutative_id = "2" * 32
    (commutative_store.diagram_dir / f"{commutative_id}.commutative.json").write_text(
        json.dumps(
            {
                "version": 1,
                "name": "Broken arrows",
                "width": 70,
                "nodes": [{"id": "a", "label": "A", "row": 0, "column": 0}],
                "arrows": [{"source": "a", "target": "missing", "label": ""}],
            }
        ),
        encoding="utf-8",
    )
    _append_asset(
        commutative_store,
        commutative_entry["id"],
        {
            "id": commutative_id,
            "kind": "commutative",
            "source": f"diagrams/{commutative_id}.commutative.json",
            "alt": "Broken arrows",
            "width": 70,
        },
    )
    with pytest.raises(StoreError, match="unknown arrow endpoint"):
        commutative_store.snapshot()
